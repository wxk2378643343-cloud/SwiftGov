import json
import os
import random
from math import ceil
from datetime import datetime
from time import time

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .models import (
    Announcement,
    Application,
    Feedback,
    FlowLog,
    Material,
    Notification,
    OperationLog,
    ServiceItem,
    User,
    Verification,
)
from .schemas import (
    AdminUserCreate,
    AdminUserUpdate,
    AnnouncementCreate,
    ApplicationCreate,
    ApplicationUpdate,
    FeedbackInput,
    LoginInput,
    PasswordUpdate,
    ProfileUpdate,
    ServiceCreate,
    StaffActionInput,
    UserCreate,
    UserOut,
    VerificationInput,
    VerificationOut,
)
from .security import create_access_token, decode_access_token, hash_password, verify_password
from .seed import seed_data

app = FastAPI(title="SwiftGov Secure API", version="1.0.0")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://127.0.0.1:5174,http://localhost:5174"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in ALLOWED_ORIGINS if x.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

LOGIN_ATTEMPTS: dict[str, list[float]] = {}


STATUS_NAMES = {
    "draft": "草稿",
    "submitted": "已提交",
    "pending_accept": "待受理",
    "correction_required": "补正中",
    "pending_review": "审核中",
    "pending_approval": "待审批",
    "approved": "已审批",
    "rejected": "已驳回",
    "withdrawn": "已撤回",
    "completed": "已办结",
}

ROLE_PERMISSIONS = {
    "resident": [
        "message:view",
        "service:view",
        "application:create",
        "application:update",
        "application:submit",
        "application:withdraw",
        "feedback:create",
        "announcement:view",
        "profile:update",
    ],
    "admin": [
        "dashboard:view",
        "stats:view",
        "message:view",
        "service:view",
        "service:create",
        "service:update",
        "application:view",
        "workflow:view",
        "workflow:accept",
        "workflow:request_correction",
        "workflow:reject",
        "workflow:review",
        "workflow:approve",
        "workflow:complete",
        "announcement:view",
        "announcement:create",
        "announcement:update",
        "announcement:delete",
        "feedback:view",
        "user:view",
        "user:create",
        "user:update",
        "profile:update",
    ],
}


def app_no() -> str:
    return f"SG{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"


def add_log(
    db: Session,
    application_id: int,
    from_status: str,
    to_status: str,
    user: User | None,
    comment: str = "",
):
    db.add(
        FlowLog(
            application_id=application_id,
            from_status=from_status,
            to_status=to_status,
            operator_id=user.id if user else None,
            operator_role=user.role if user else "system",
            comment=comment,
        )
    )


def notify(db: Session, user_id: int, title: str, content: str):
    db.add(Notification(user_id=user_id, title=title, content=content))


def log_op(db: Session, user: User | None, module: str, action: str, detail: str = ""):
    db.add(
        OperationLog(
            user_id=user.id if user else None,
            username=user.username if user else None,
            role=user.role if user else None,
            module=module,
            action=action,
            detail=detail,
        )
    )


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="请先登录")

    token = authorization.replace("Bearer ", "").strip()
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id or not str(user_id).isdigit():
        raise HTTPException(status_code=401, detail="令牌无效")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_roles(user: User, roles: list[str]):
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="权限不足")


def get_permissions(role: str) -> list[str]:
    return ROLE_PERMISSIONS.get(role, [])


def require_permission(user: User, permission: str):
    if permission not in get_permissions(user.role):
        raise HTTPException(status_code=403, detail=f"缺少权限: {permission}")


def auth_payload(user: User):
    return {
        "token": create_access_token(user.id, user.role),
        "user": UserOut.model_validate(user),
        "permissions": get_permissions(user.role),
    }


def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="密码长度至少8位")
    has_alpha = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_alpha and has_digit):
        raise HTTPException(status_code=400, detail="密码需包含字母和数字")


def check_login_rate_limit(key: str):
    now = time()
    arr = LOGIN_ATTEMPTS.setdefault(key, [])
    arr[:] = [t for t in arr if now - t < 60]
    if len(arr) >= 8:
        raise HTTPException(status_code=429, detail="登录尝试过于频繁，请稍后再试")


def add_login_failure(key: str):
    LOGIN_ATTEMPTS.setdefault(key, []).append(time())


def clear_login_failure(key: str):
    LOGIN_ATTEMPTS.pop(key, None)


def paginate_query(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, ceil(total / page_size)) if page_size else 1,
    }


def paginate_list(items: list, page: int, page_size: int):
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, ceil(total / page_size)) if page_size else 1,
    }


def application_payload(item: Application):
    return {
        "id": item.id,
        "app_no": item.app_no,
        "status": item.status,
        "status_name": STATUS_NAMES.get(item.status, item.status),
        "service": {
            "id": item.service.id,
            "name": item.service.name,
            "category": item.service.category,
        },
        "form_data": json.loads(item.form_data or "{}"),
        "result_text": item.result_text,
        "result_file": item.result_file,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "submitted_at": item.submitted_at,
        "finished_at": item.finished_at,
    }


@app.get("/api/health")
def health():
    return {"ok": True, "service": "swiftgov-secure"}


@app.post("/api/auth/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    validate_password(data.password)
    user = User(
        username=data.username,
        password=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        id_card=data.id_card,
        role="resident",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_op(db, user, "auth", "register", f"new user {user.username}")
    db.commit()
    return auth_payload(user)


@app.post("/api/auth/login")
def login(data: LoginInput, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    limit_key = f"{client_ip}:{data.username}"
    check_login_rate_limit(limit_key)
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        add_login_failure(limit_key)
        raise HTTPException(status_code=400, detail="账号或密码错误")

    clear_login_failure(limit_key)
    log_op(db, user, "auth", "login", "user login")
    db.commit()
    return auth_payload(user)


@app.get("/api/users/me")
def me(user: User = Depends(current_user)):
    return {"user": UserOut.model_validate(user), "permissions": get_permissions(user.role)}


@app.put("/api/users/me")
def update_me(
    data: ProfileUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "profile:update")
    user.full_name = data.full_name
    user.phone = data.phone
    user.id_card = data.id_card
    log_op(db, user, "profile", "update", user.username)
    db.commit()
    db.refresh(user)
    return {"user": UserOut.model_validate(user), "permissions": get_permissions(user.role)}


@app.put("/api/users/me/password")
def update_my_password(
    data: PasswordUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "profile:update")
    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="原密码错误")
    validate_password(data.new_password)
    user.password = hash_password(data.new_password)
    log_op(db, user, "profile", "change_password", user.username)
    db.commit()
    return {"ok": True}


@app.post("/api/verification/submit")
def submit_verification(
    data: VerificationInput,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    verify = db.query(Verification).filter(Verification.user_id == user.id).first()
    if not verify:
        verify = Verification(user_id=user.id)
        db.add(verify)

    verify.submitted_name = data.submitted_name
    verify.submitted_id_card = data.submitted_id_card
    # 脆弱版简化: 提交后直接通过认证
    verify.status = "approved"
    verify.remark = "认证通过"

    db.commit()
    db.refresh(verify)
    return VerificationOut.model_validate(verify)


@app.get("/api/verification/me")
def my_verification(user: User = Depends(current_user), db: Session = Depends(get_db)):
    verify = db.query(Verification).filter(Verification.user_id == user.id).first()
    if not verify:
        return {"status": "unverified"}
    return VerificationOut.model_validate(verify)


@app.get("/api/public/home")
def home(db: Session = Depends(get_db)):
    hot_services = (
        db.query(ServiceItem)
        .filter(ServiceItem.is_hot == True, ServiceItem.status == "enabled")
        .order_by(ServiceItem.created_at.desc())
        .limit(6)
        .all()
    )
    announcements = (
        db.query(Announcement)
        .order_by(Announcement.is_top.desc(), Announcement.created_at.desc())
        .limit(8)
        .all()
    )
    return {"hot_services": hot_services, "announcements": announcements}


@app.get("/api/services")
def list_services(
    keyword: str | None = None,
    category: str | None = None,
    department: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(ServiceItem).filter(ServiceItem.status == "enabled")
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(ServiceItem.name.like(like) | ServiceItem.description.like(like))
    if category:
        q = q.filter(ServiceItem.category == category)
    if department:
        q = q.filter(ServiceItem.department == department)
    return q.order_by(ServiceItem.is_hot.desc(), ServiceItem.created_at.desc()).all()


@app.get("/api/services/{service_id}")
def service_detail(service_id: int, db: Session = Depends(get_db)):
    item = db.query(ServiceItem).filter(ServiceItem.id == service_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="事项不存在")
    return item


@app.post("/api/applications")
def create_application(
    data: ApplicationCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "application:create")
    verify = db.query(Verification).filter(Verification.user_id == user.id).first()
    if not verify or verify.status != "approved":
        raise HTTPException(status_code=400, detail="请先完成实名认证")

    service = db.query(ServiceItem).filter(ServiceItem.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="事项不存在")

    status = "pending_accept" if data.submit_now else "draft"
    item = Application(
        app_no=app_no(),
        user_id=user.id,
        service_id=data.service_id,
        status=status,
        form_data=json.dumps(data.form_data, ensure_ascii=False),
        submitted_at=datetime.utcnow() if data.submit_now else None,
    )
    db.add(item)
    db.flush()

    for m in data.materials:
        db.add(
            Material(
                application_id=item.id,
                name=m.name,
                file_name=m.file_name,
                file_size=m.file_size,
            )
        )

    add_log(db, item.id, "new", status, user, "新建申请")
    if data.submit_now:
        notify(db, user.id, "申请已提交", f"申请编号 {item.app_no} 已提交，等待受理。")
    log_op(db, user, "application", "create", f"{item.app_no} status={status}")
    db.commit()
    db.refresh(item)
    return application_payload(item)


@app.put("/api/applications/{app_id}")
def update_application(
    app_id: int,
    data: ApplicationUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "application:update")
    item = db.query(Application).filter(Application.id == app_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="申请不存在")
    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="仅可修改本人申请")
    if item.status not in ["draft", "correction_required"]:
        raise HTTPException(status_code=400, detail="当前状态不可编辑")

    old = item.status
    item.form_data = json.dumps(data.form_data, ensure_ascii=False)
    db.query(Material).filter(Material.application_id == item.id).delete()
    for m in data.materials:
        db.add(
            Material(
                application_id=item.id,
                name=m.name,
                file_name=m.file_name,
                file_size=m.file_size,
            )
        )
    add_log(db, item.id, old, old, user, "更新申请内容")
    db.commit()
    db.refresh(item)
    return application_payload(item)


@app.post("/api/applications/{app_id}/submit")
def submit_application(
    app_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "application:submit")
    item = db.query(Application).filter(Application.id == app_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="申请不存在")
    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="仅可提交本人申请")
    if item.status not in ["draft", "correction_required"]:
        raise HTTPException(status_code=400, detail="当前状态不可提交")

    old = item.status
    item.status = "pending_accept"
    item.submitted_at = datetime.utcnow()
    add_log(db, item.id, old, "pending_accept", user, "提交申请")
    notify(db, user.id, "申请已提交", f"申请编号 {item.app_no} 已进入待受理。")
    log_op(db, user, "application", "submit", item.app_no)
    db.commit()
    db.refresh(item)
    return application_payload(item)


@app.post("/api/applications/{app_id}/withdraw")
def withdraw_application(
    app_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "application:withdraw")
    item = db.query(Application).filter(Application.id == app_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="申请不存在")
    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="仅可撤回本人申请")
    if item.status not in ["pending_accept", "pending_review"]:
        raise HTTPException(status_code=400, detail="当前状态不可撤回")

    old = item.status
    item.status = "withdrawn"
    add_log(db, item.id, old, "withdrawn", user, "居民主动撤回")
    log_op(db, user, "application", "withdraw", item.app_no)
    db.commit()
    return {"ok": True}


@app.get("/api/applications/my")
def my_applications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Application)
        .filter(Application.user_id == user.id)
        .order_by(Application.updated_at.desc())
    )
    result = paginate_query(q, page, page_size)
    return {
        **result,
        "items": [application_payload(item) for item in result["items"]],
    }


@app.get("/api/applications/{app_id}")
def application_detail(
    app_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    item = db.query(Application).filter(Application.id == app_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="申请不存在")
    if user.role == "resident" and item.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权查看该申请")

    payload = application_payload(item)
    payload["materials"] = item.materials
    payload["flow_logs"] = sorted(item.flow_logs, key=lambda i: i.created_at, reverse=False)
    return payload


@app.get("/api/progress/{app_no}")
def progress(app_no: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.query(Application).filter(Application.app_no == app_no).first()
    if not item:
        raise HTTPException(status_code=404, detail="申请编号不存在")
    if user.role == "resident" and item.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权查看进度")
    return application_detail(item.id, user, db)


@app.get("/api/messages")
def my_messages(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "message:view")
    q = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
    )
    return paginate_query(q, page, page_size)


@app.post("/api/messages/{msg_id}/read")
def read_message(msg_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    msg = db.query(Notification).filter(Notification.id == msg_id).first()
    if not msg or msg.user_id != user.id:
        raise HTTPException(status_code=404, detail="消息不存在")
    msg.is_read = True
    db.commit()
    return {"ok": True}


@app.get("/api/messages/unread-count")
def unread_count(user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_permission(user, "message:view")
    count = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == user.id, Notification.is_read == False)
        .scalar()
        or 0
    )
    return {"unread": int(count)}


@app.post("/api/feedback")
def create_feedback(
    data: FeedbackInput,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "feedback:create")
    item = db.query(Application).filter(Application.id == data.application_id).first()
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="申请不存在")
    if item.status != "completed":
        raise HTTPException(status_code=400, detail="仅办结后可评价")
    db.add(
        Feedback(
            application_id=data.application_id,
            user_id=user.id,
            rating=data.rating,
            comment=data.comment,
        )
    )
    db.commit()
    return {"ok": True}


@app.get("/api/announcements")
def list_announcements(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "announcement:view")
    q = db.query(Announcement).order_by(Announcement.is_top.desc(), Announcement.created_at.desc())
    return paginate_query(q, page, page_size)


@app.get("/api/staff/applications")
def staff_applications(
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "workflow:view")
    q = db.query(Application)
    if status:
        q = q.filter(Application.status == status)
    q = q.order_by(Application.updated_at.desc())
    result = paginate_query(q, page, page_size)
    return {
        **result,
        "items": [application_payload(item) for item in result["items"]],
    }


@app.post("/api/staff/applications/{app_id}/action")
def staff_action(
    app_id: int,
    data: StaffActionInput,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "workflow:view")
    item = db.query(Application).filter(Application.id == app_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="申请不存在")

    old = item.status
    action_map = {
        "accept": "pending_review",
        "request_correction": "correction_required",
        "reject": "rejected",
        "review_pass": "pending_approval",
        "review_reject": "rejected",
        "approve": "approved",
        "complete": "completed",
    }
    if data.action not in action_map:
        raise HTTPException(status_code=400, detail="不支持的操作")
    action_permission_map = {
        "accept": "workflow:accept",
        "request_correction": "workflow:request_correction",
        "reject": "workflow:reject",
        "review_pass": "workflow:review",
        "review_reject": "workflow:review",
        "approve": "workflow:approve",
        "complete": "workflow:complete",
    }
    require_permission(user, action_permission_map[data.action])

    item.status = action_map[data.action]
    if data.action == "complete":
        item.result_text = data.result_text or "审批通过，事项已办结。"
        item.result_file = data.result_file or "result-demo.pdf"
        item.finished_at = datetime.utcnow()

    add_log(db, item.id, old, item.status, user, data.comment or data.action)
    notify(
        db,
        item.user_id,
        "办理状态更新",
        f"申请 {item.app_no} 状态已更新为 {STATUS_NAMES.get(item.status, item.status)}。",
    )
    log_op(db, user, "workflow", data.action, f"{item.app_no}: {old} -> {item.status}")
    db.commit()
    db.refresh(item)
    return application_payload(item)


@app.post("/api/admin/services")
def create_service(
    data: ServiceCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "service:create")
    service = ServiceItem(**data.model_dump())
    db.add(service)
    log_op(db, user, "service", "create", service.name)
    db.commit()
    db.refresh(service)
    return service


@app.put("/api/admin/services/{service_id}")
def update_service(
    service_id: int,
    data: ServiceCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "service:update")
    service = db.query(ServiceItem).filter(ServiceItem.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="事项不存在")
    for k, v in data.model_dump().items():
        setattr(service, k, v)
    log_op(db, user, "service", "update", f"{service.id}:{service.name}")
    db.commit()
    db.refresh(service)
    return service


@app.post("/api/admin/announcements")
def create_announcement(
    data: AnnouncementCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "announcement:create")
    row = Announcement(**data.model_dump())
    db.add(row)
    log_op(db, user, "announcement", "create", row.title)
    db.commit()
    db.refresh(row)
    return row


@app.put("/api/admin/announcements/{ann_id}")
def update_announcement(
    ann_id: int,
    data: AnnouncementCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "announcement:update")
    row = db.query(Announcement).filter(Announcement.id == ann_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="公告不存在")
    row.title = data.title
    row.content = data.content
    row.is_top = data.is_top
    db.commit()
    db.refresh(row)
    return row


@app.delete("/api/admin/announcements/{ann_id}")
def delete_announcement(
    ann_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "announcement:delete")
    row = db.query(Announcement).filter(Announcement.id == ann_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="公告不存在")
    db.delete(row)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/users")
def admin_users(
    keyword: str | None = None,
    role: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "user:view")
    q = db.query(User)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(User.username.like(like) | User.full_name.like(like))
    if role:
        q = q.filter(User.role == role)
    q = q.order_by(User.id.desc())
    result = paginate_query(q, page, page_size)
    return {
        **result,
        "items": [
            {
                "id": r.id,
                "username": r.username,
                "full_name": r.full_name,
                "phone": r.phone,
                "id_card": r.id_card,
                "role": r.role,
                "created_at": r.created_at,
            }
            for r in result["items"]
        ],
    }


@app.post("/api/admin/users")
def admin_create_user(
    data: AdminUserCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "user:create")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    validate_password(data.password)
    row = User(
        username=data.username,
        password=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        id_card=data.id_card,
        role=data.role,
    )
    db.add(row)
    log_op(db, user, "user", "create", row.username)
    db.commit()
    db.refresh(row)
    return row


@app.put("/api/admin/users/{user_id}")
def admin_update_user(
    user_id: int,
    data: AdminUserUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "user:update")
    row = db.query(User).filter(User.id == user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="用户不存在")
    row.full_name = data.full_name
    row.phone = data.phone
    row.id_card = data.id_card
    row.role = data.role
    if data.password:
        validate_password(data.password)
        row.password = hash_password(data.password)
    log_op(db, user, "user", "update", row.username)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/admin/roles")
def admin_roles(user: User = Depends(current_user)):
    require_permission(user, "user:view")
    return [
        {"code": "resident", "name": "居民用户"},
        {"code": "admin", "name": "系统管理员"},
    ]


@app.get("/api/admin/departments")
def admin_departments(user: User = Depends(current_user)):
    require_permission(user, "user:view")
    return [
        {"code": "public_security", "name": "公安分局"},
        {"code": "civil_affairs", "name": "民政局"},
        {"code": "hrss", "name": "人社局"},
        {"code": "gov_service", "name": "政务服务中心"},
    ]


@app.get("/api/admin/services")
def admin_services(
    keyword: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_roles(user, ["admin"])
    q = db.query(ServiceItem)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(ServiceItem.name.like(like))
    q = q.order_by(ServiceItem.id.desc())
    return paginate_query(q, page, page_size)


@app.get("/api/admin/feedbacks")
def admin_feedbacks(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_roles(user, ["admin"])
    rows = db.query(Feedback).order_by(Feedback.created_at.desc())
    paged = paginate_query(rows, page, page_size)
    out = []
    for r in paged["items"]:
        app_item = db.query(Application).filter(Application.id == r.application_id).first()
        resident = db.query(User).filter(User.id == r.user_id).first()
        out.append(
            {
                "id": r.id,
                "application_id": r.application_id,
                "app_no": app_item.app_no if app_item else "",
                "service_name": app_item.service.name if app_item else "",
                "resident_name": resident.full_name if resident else "",
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at,
            }
        )
    return {
        **paged,
        "items": out,
    }


@app.get("/api/admin/logs")
def admin_logs(
    module: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_roles(user, ["admin"])
    q = db.query(OperationLog)
    if module:
        q = q.filter(OperationLog.module == module)
    return q.order_by(OperationLog.created_at.desc()).limit(500).all()


@app.get("/api/admin/stats")
def stats(user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_permission(user, "stats:view")
    total = db.query(func.count(Application.id)).scalar() or 0
    completed = db.query(func.count(Application.id)).filter(Application.status == "completed").scalar() or 0
    correction = (
        db.query(func.count(Application.id)).filter(Application.status == "correction_required").scalar() or 0
    )
    rejected = db.query(func.count(Application.id)).filter(Application.status == "rejected").scalar() or 0
    avg_days = (
        db.query(func.avg(func.julianday(Application.finished_at) - func.julianday(Application.submitted_at)))
        .filter(Application.finished_at.is_not(None), Application.submitted_at.is_not(None))
        .scalar()
    )
    satisfaction = db.query(func.avg(Feedback.rating)).scalar() or 0
    return {
        "total_applications": total,
        "completed": completed,
        "correction_required": correction,
        "rejected": rejected,
        "avg_process_days": round(float(avg_days or 0), 2),
        "avg_satisfaction": round(float(satisfaction), 2),
    }


@app.get("/api/admin/stats/overview")
def stats_overview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return stats(user, db)


@app.get("/api/admin/stats/status-distribution")
def stats_status_distribution(user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_permission(user, "stats:view")
    rows = db.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    return [{"status": k, "name": STATUS_NAMES.get(k, k), "count": v} for k, v in rows]


@app.get("/api/admin/stats/service-ranking")
def stats_service_ranking(user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_permission(user, "stats:view")
    rows = (
        db.query(ServiceItem.name, func.count(Application.id).label("count"))
        .join(Application, Application.service_id == ServiceItem.id)
        .group_by(ServiceItem.name)
        .order_by(func.count(Application.id).desc())
        .limit(10)
        .all()
    )
    return [{"name": k, "count": v} for k, v in rows]


@app.get("/api/admin/stats/trend")
def stats_trend(
    days: int = Query(default=7, ge=7, le=90),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "stats:view")
    rows = (
        db.query(func.strftime("%Y-%m-%d", Application.created_at).label("day"), func.count(Application.id))
        .group_by("day")
        .order_by("day")
        .all()
    )
    points = [{"day": day, "count": count} for day, count in rows]
    return points[-days:]
