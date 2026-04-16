from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    phone: str
    id_card: str | None = None


class AdminUserCreate(UserCreate):
    role: str = "resident"


class AdminUserUpdate(BaseModel):
    full_name: str
    phone: str
    id_card: str | None = None
    role: str = "resident"
    password: str | None = None


class ProfileUpdate(BaseModel):
    full_name: str
    phone: str
    id_card: str | None = None


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class LoginInput(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    phone: str
    id_card: str | None
    role: str
    created_at: datetime


class VerificationInput(BaseModel):
    submitted_name: str
    submitted_id_card: str


class VerificationOut(BaseModel):
    status: str
    submitted_name: str | None = None
    submitted_id_card: str | None = None
    remark: str | None = None
    updated_at: datetime | None = None


class ServiceCreate(BaseModel):
    name: str
    category: str
    department: str
    description: str
    conditions: str
    materials: str
    processing_days: int = 5
    fee: str = "免费"
    is_online: bool = True
    is_hot: bool = False
    status: str = "enabled"


class ServiceOut(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class MaterialInput(BaseModel):
    name: str
    file_name: str
    file_size: int = 0


class ApplicationCreate(BaseModel):
    service_id: int
    form_data: dict[str, Any] = Field(default_factory=dict)
    materials: list[MaterialInput] = Field(default_factory=list)
    submit_now: bool = False


class ApplicationUpdate(BaseModel):
    form_data: dict[str, Any] = Field(default_factory=dict)
    materials: list[MaterialInput] = Field(default_factory=list)


class FlowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_status: str
    to_status: str
    operator_role: str | None = None
    comment: str | None = None
    created_at: datetime


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    app_no: str
    user_id: int
    service_id: int
    status: str
    form_data: str
    result_text: str | None = None
    result_file: str | None = None
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None = None
    finished_at: datetime | None = None


class StaffActionInput(BaseModel):
    action: str
    comment: str = ""
    result_text: str | None = None
    result_file: str | None = None


class FeedbackInput(BaseModel):
    application_id: int
    rating: int = Field(ge=1, le=5)
    comment: str


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    is_top: bool = False
