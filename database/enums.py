from enum import Enum


class Status(str, Enum):
    in_review = "in_review",
    rejected = "rejected",
    approved = "approved",
    deleted = "deleted",
    finished = "finished"


class Role(str, Enum):
    main_admin = "main_admin",
    admin = "admin",
    user = "user",
    admins = [main_admin, admin]
