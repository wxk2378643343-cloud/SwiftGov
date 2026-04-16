from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    username = mapped_column(String(50), unique=True, index=True, nullable=False)
    password = mapped_column(String(128), nullable=False)
    full_name = mapped_column(String(50), nullable=False)
    phone = mapped_column(String(30), nullable=False)
    id_card = mapped_column(String(30), nullable=True)
    role = mapped_column(String(20), default="resident", nullable=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    verification = relationship("Verification", back_populates="user", uselist=False)


class Verification(Base):
    __tablename__ = "verifications"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    status = mapped_column(String(20), default="unverified", nullable=False)
    submitted_name = mapped_column(String(50), nullable=True)
    submitted_id_card = mapped_column(String(30), nullable=True)
    remark = mapped_column(String(200), nullable=True)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="verification")


class ServiceItem(Base):
    __tablename__ = "service_items"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String(120), nullable=False)
    category = mapped_column(String(50), nullable=False)
    department = mapped_column(String(80), nullable=False)
    description = mapped_column(Text, nullable=False)
    conditions = mapped_column(Text, nullable=False)
    materials = mapped_column(Text, nullable=False)
    processing_days = mapped_column(Integer, default=5)
    fee = mapped_column(String(50), default="免费")
    is_online = mapped_column(Boolean, default=True)
    is_hot = mapped_column(Boolean, default=False)
    status = mapped_column(String(20), default="enabled")
    created_at = mapped_column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"

    id = mapped_column(Integer, primary_key=True, index=True)
    app_no = mapped_column(String(40), unique=True, index=True, nullable=False)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = mapped_column(Integer, ForeignKey("service_items.id"), nullable=False)
    status = mapped_column(String(30), default="draft", nullable=False)
    form_data = mapped_column(Text, nullable=False)
    result_text = mapped_column(Text, nullable=True)
    result_file = mapped_column(String(255), nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = mapped_column(DateTime, nullable=True)
    finished_at = mapped_column(DateTime, nullable=True)

    user = relationship("User")
    service = relationship("ServiceItem")
    flow_logs = relationship("FlowLog", back_populates="application", cascade="all, delete-orphan")
    materials = relationship("Material", back_populates="application", cascade="all, delete-orphan")


class Material(Base):
    __tablename__ = "materials"

    id = mapped_column(Integer, primary_key=True, index=True)
    application_id = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    name = mapped_column(String(120), nullable=False)
    file_name = mapped_column(String(150), nullable=False)
    file_size = mapped_column(Integer, default=0)
    status = mapped_column(String(20), default="uploaded")
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="materials")


class FlowLog(Base):
    __tablename__ = "flow_logs"

    id = mapped_column(Integer, primary_key=True, index=True)
    application_id = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    from_status = mapped_column(String(30), nullable=False)
    to_status = mapped_column(String(30), nullable=False)
    operator_id = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    operator_role = mapped_column(String(20), nullable=True)
    comment = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="flow_logs")


class Notification(Base):
    __tablename__ = "notifications"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title = mapped_column(String(100), nullable=False)
    content = mapped_column(Text, nullable=False)
    is_read = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)


class Announcement(Base):
    __tablename__ = "announcements"

    id = mapped_column(Integer, primary_key=True, index=True)
    title = mapped_column(String(120), nullable=False)
    content = mapped_column(Text, nullable=False)
    is_top = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = mapped_column(Integer, primary_key=True, index=True)
    application_id = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    rating = mapped_column(Integer, nullable=False)
    comment = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    username = mapped_column(String(50), nullable=True)
    role = mapped_column(String(20), nullable=True)
    module = mapped_column(String(50), nullable=False)
    action = mapped_column(String(50), nullable=False)
    detail = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
