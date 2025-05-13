from datetime import timedelta

from fastapi import HTTPException, Body, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from starlette import status
from starlette.requests import Request

from API.api.auth import get_current_user, Token, validate_token, create_tokens, \
    authenticate_user, pwd_context, REFRESH_SECRET_KEY, ALGORITHM
from API.api import UserCreateRequest, EventCreateRequest, UserRequest, EventCreateDescription
from API.app import app
from database.context import repository
from database.models import User
from database.repository.repository import Repository

"""
На будущее: всегда используй это
Асинхронные запросы в бд вне репозиториев через репозитории :)
    @app.get("/user/{user_id}")
    async def get_user(user_id: int, repo: Repository = Depends(repository)):
        return (await repo.user.get(user_id)).dict()
"""


@app.post("/users", response_model=UserRequest)
async def create_user(user_data: UserCreateRequest, repo: Repository = Depends(repository)):
    user = await repo.user.create_user(username=user_data.username,
                                       login=user_data.login,
                                       password=pwd_context.hash(user_data.password))
    return user.dict()


@app.get("/user/{user_id}")
async def get_user(user_id: int, repo: Repository = Depends(repository)):
    return (await repo.user.get(user_id)).dict()


@app.get("/user/{limit}")
async def get_users_by_limit(limit: int, repo: Repository = Depends(repository)):
    users = (await repo.user.get_by_limit(limit))
    return [user.dict() for user in users]


@app.post("/events", response_model=EventCreateRequest)
async def create_event(event_data: EventCreateDescription,
                       current_user: User = Depends(get_current_user),
                       repo: Repository = Depends(repository)):
    event = await repo.event.create_event(creator=current_user,
                                          title=event_data.title,
                                          description=event_data.description,
                                          date=event_data.date,
                                          limit_visitors=event_data.limit_visitors,
                                          location=event_data.location,
                                          )
    return event.dict()


@app.get("/event/{event_id}")
async def get_event(event_id: int, repo: Repository = Depends(repository)):
    return (await repo.event.get(event_id)).dict()


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
    access_token, refresh_token = create_tokens(user.login)

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

        user = await repo.user.get_by_login(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_access_token = create_tokens(user.login)[0]
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")



@app.get("/users/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user.dict()


"""
Переделать под наш проект

from orders.orders_service.exceptions import OrderNotFoundError
from orders.orders_service.orders_service import OrdersService
from orders.repository.orders_repository import OrdersRepository
from orders.repository.unit_of_work import UnitOfWork
from orders.web.app import app
from orders.web.api.schemas import GetOrderSchema, CreateOrderSchema, GetOrdersSchema


@app.get("/orders", response_model=GetOrdersSchema)
def get_orders(
    request: Request, cancelled: Optional[bool] = None, limit: Optional[int] = None
):
    with UnitOfWork() as unit_of_work:
        repo = OrdersRepository(unit_of_work.session)
        orders_service = OrdersService(repo)
        results = orders_service.list_orders(
            limit=limit, cancelled=cancelled, user_id=request.state.user_id
        )
    return {"orders": [result.dict() for result in results]}

@app.get("/users", response_model=GetUsersSchema)
def get_users(
    request: Request, limit: Optional[int] = None
):
    

@app.post("/orders", status_code=status.HTTP_201_CREATED, response_model=GetOrderSchema)
def create_order(request: Request, payload: CreateOrderSchema):
    with UnitOfWork() as unit_of_work:
        repo = OrdersRepository(unit_of_work.session)
        orders_service = OrdersService(repo)
        order = payload.dict()["order"]
        for item in order:
            item["size"] = item["size"].value
        order = orders_service.place_order(order, request.state.user_id)
        unit_of_work.commit()
        return_payload = order.dict()
    return return_payload


@app.get("/orders/{order_id}", response_model=GetOrderSchema)
def get_order(request: Request, order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = orders_service.get_order(
                order_id=order_id, user_id=request.state.user_id
            )
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )


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
