from datetime import timedelta

from fastapi import HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from starlette import status
from starlette.requests import Request

from API.api.auth import get_current_user, Token, create_tokens, \
    authenticate_user, pwd_context, REFRESH_SECRET_KEY, ALGORITHM
from API.api import UserCreateRequest, UserRequest, \
    EventCreateDescription, EventResponse, StatusSchema, EditEventSchema, \
    AdminEditEventSchema
from API.app import app
from database.context import repository
from database.enums import Status, Role
from database.models.safe_user import SafeUser
from database.repository.repository import Repository

"""
На будущее: всегда используй это
Асинхронные запросы в бд вне репозиториев через репозитории :)
    @app.get("/user/{user_id}")
    async def get_user(user_id: int, repo: Repository = Depends(repository)):
        return (await repo.user.get(user_id)).dict()
"""


@app.get("/")
async def i_am_teapot():
    raise HTTPException(
        418,
        detail="I'm teapot and you are teapot"
    )


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserRequest)
async def create_user(user_data: UserCreateRequest, repo: Repository = Depends(repository)):
    # потом сделать проверку на уже наличие такого пользователя.
    user = await repo.user.create_user(username=user_data.username,
                                       nickname=user_data.nickname,
                                       password=pwd_context.hash(user_data.password))
    return user.dict()


@app.get("/user/{user_id}")
async def get_user(user_id: int, repo: Repository = Depends(repository)):
    return (await repo.user.get(user_id)).dict()


@app.get("/users")
async def get_all_users(repo: Repository = Depends(repository)):
    users = (await repo.user.get_all())
    return [user.dict() for user in users]


@app.post("/events", status_code=status.HTTP_201_CREATED, response_model=EventResponse)
async def create_event(event_data: EventCreateDescription,
                       current_user: SafeUser = Depends(get_current_user),
                       repo: Repository = Depends(repository)):
    event = await repo.event.create_event(creator=current_user,
                                          title=event_data.title,
                                          description=event_data.description,
                                          date=event_data.date,
                                          limit_visitors=event_data.limit_visitors,
                                          location=event_data.location,
                                          )
    return event.dict()


@app.get("/events")
async def get_all_events(repo: Repository = Depends(repository)):
    events = await repo.event.get_all()
    return events


@app.get("/event/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, repo: Repository = Depends(repository)):
    event = await repo.event.get(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    if event.status == Status.deleted:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Event was deleted",
            headers={
                "message": "Event was deleted",
                "event": event.dict()
            },
        )
    return event.dict()


@app.get("/event/{event_title}")
async def get_event_by_title(event_title: str, repo: Repository = Depends(repository)):
    events = await repo.event.get_by_title(event_title)
    return [event.dict() for event in events]


@app.post("/auth/login", response_model=Token)
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        repo: Repository = Depends(repository)
):
    # Аутентификация пользователя
    user = await authenticate_user(form_data.username, form_data.password, repo)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Создаем токены
    access_token, refresh_token = create_tokens(user.username)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Только для HTTPS
        samesite="lax",
        max_age=int(timedelta(days=30).total_seconds()),
        path="/auth/refresh"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/auth/refresh", response_model=Token)
async def refresh_token(
        request: Request,
        repo: Repository = Depends(repository)
):
    # Валидация refresh токена
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing"
        )
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        user = await repo.user.get_safe_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_access_token = create_tokens(user.username)[0]
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@app.get("/users/me")
async def read_current_user(current_user: SafeUser = Depends(get_current_user)):
    return current_user.dict()


@app.put("/user/{user_id}/role")
async def edit_role(user_id: int,
                    current_user: SafeUser = Depends(get_current_user),
                    repo: Repository = Depends(repository)):
    if current_user.role != Role.main_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough rights",
        )


@app.put("/event/{event_id}/sign_up")
async def sign_up_on_event(event_id: int,
                           current_user: SafeUser = Depends(get_current_user),
                           repo: Repository = Depends(repository)):
    event = await repo.event.get(event_id)

    if current_user.user_id == event.creator_id:
        raise HTTPException(
            status_code=400,
            detail="The user is the organizer of the event"
        )

    # Проверяем, не записан ли уже пользователь
    if current_user in event.visitors:
        raise HTTPException(400, "User already signed up")

    # Проверяем лимит участников
    if len(event.visitors) >= event.limit_visitors:
        raise HTTPException(400, "Event is full")

    event.visitors.append(current_user)
    await repo.commit()

    return {"message": "Successfully signed up"}


@app.put("/event/{event_id}/sign_out")
async def sign_out_from_event(event_id: int,
                              current_user: SafeUser = Depends(get_current_user),
                              repo: Repository = Depends(repository)):
    event = await repo.event.get(event_id)
    # Проверяем, не записан ли уже пользователь
    if current_user not in event.visitors:
        raise HTTPException(400, "User already signed out")

    event.visitors.remove(current_user)
    await repo.commit()

    return {"message": "Successfully signed out"}


@app.get("/event/{event_id}/visitors")
async def check_visitors(event_id: int,
                         repo: Repository = Depends(repository)):
    event = await repo.event.get(event_id)
    return event.visitors


@app.put("/event/{event_id}/status")
async def update_status_event(event_id: int,
                              data: StatusSchema,
                              current_user: SafeUser = Depends(get_current_user),
                              repo: Repository = Depends(repository)):
    event = await repo.event.get(event_id)
    if current_user.role not in Role.admins:
        raise HTTPException(
            status_code=403,
            detail="The user is not an admin"
        )
    match data.verdict:
        case Status.rejected:
            event.status = Status.rejected
        case Status.approved:
            event.status = Status.approved
        case Status.deleted:
            event.status = Status.deleted
        case Status.finished:
            event.status = Status.finished


@app.put("/event/{event_id}/edit")
async def edit_event(event_id: int,
                     data: EditEventSchema,
                     current_user: SafeUser = Depends(get_current_user),
                     repo: Repository = Depends(repository)):
    event = await repo.event.get(event_id)
    if event.creator_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="The user is not the creator of this event"
        )
    if data.title:
        event.title = data.title
    if data.description:
        event.description = data.description
    if data.date:
        event.date = data.date
    if data.limit_visitors:
        event.limit_visitors = data.limit_visitors
    if data.location:
        event.location = data.location
    await repo.commit()
    return {"message": "Edited successfully "}


@app.put("/event/{event_id}/admin_edit")
async def admin_edit_event(event_id: int,
                           data: AdminEditEventSchema,
                           current_user: SafeUser = Depends(get_current_user),
                           repo: Repository = Depends(repository)):
    event = await repo.event.get(event_id)
    if current_user.role not in Role.admins:
        raise HTTPException(
            status_code=403,
            detail="The user is not an admin"
        )
    if data.title:
        event.title = data.title
    if data.description:
        event.description = data.description
    if data.date:
        event.date = data.date
    if data.limit_visitors:
        event.limit_visitors = data.limit_visitors
    if data.location:
        event.location = data.location
    if data.status:
        event.status = data.status
    await repo.commit()
    return {"message": "Edited successfully "}


"""
@app.put("/orders/{order_id}", response_model=GetOrderSchema)
def update_order(request: Request, order_id: UUID, order_details: CreateOrderSchema):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = order_details.dict()["order"]
            for item in order:
                item["size"] = item["size"].value
            order = orders_service.update_order(
                order_id=order_id, items=order, user_id=request.state.user_id
            )
            unit_of_work.commit()
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )


@app.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_order(request: Request, order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            orders_service.delete_order(order_id=order_id, user_id=request.state.user_id)
            unit_of_work.commit()
        return
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )


@app.post("/orders/{order_id}/cancel", response_model=GetOrderSchema)
def cancel_order(request: Request, order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = orders_service.cancel_order(order_id=order_id, user_id=request.state.user_id)
            unit_of_work.commit()
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )


@app.post("/orders/{order_id}/pay", response_model=GetOrderSchema)
def pay_order(request: Request, order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = orders_service.pay_order(order_id=order_id, user_id=request.state.user_id)
            unit_of_work.commit()
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )

"""
