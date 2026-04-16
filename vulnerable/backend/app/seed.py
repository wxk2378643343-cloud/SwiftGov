from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .models import Announcement, Notification, ServiceItem, User, Verification


def ensure_users(db: Session):
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            password="admin123",
            full_name="系统管理员",
            phone="13800000001",
            id_card="110101199001010011",
            role="admin",
            created_at=datetime.utcnow() - timedelta(days=30),
        )
        db.add(admin)
        db.flush()
    else:
        admin.role = "admin"

    resident = db.query(User).filter(User.username == "resident001").first()
    if not resident:
        resident = User(
            username="resident001",
            password="123456",
            full_name="测试居民",
            phone="13900000001",
            id_card="110101199901010019",
            role="resident",
            created_at=datetime.utcnow() - timedelta(days=10),
        )
        db.add(resident)
        db.flush()
    else:
        resident.role = "resident"

    # 其他历史账号统一降级为居民，避免角色混乱
    db.query(User).filter(~User.username.in_(["admin", "resident001"])).update({"role": "resident"})

    verify = db.query(Verification).filter(Verification.user_id == resident.id).first()
    if not verify:
        db.add(
            Verification(
                user_id=resident.id,
                status="approved",
                submitted_name=resident.full_name,
                submitted_id_card=resident.id_card,
                remark="种子数据认证通过",
                updated_at=datetime.utcnow(),
            )
        )
    else:
        verify.status = "approved"
        verify.submitted_name = resident.full_name
        verify.submitted_id_card = resident.id_card
        verify.remark = "种子数据认证通过"
        verify.updated_at = datetime.utcnow()

    db.commit()


def ensure_services(db: Session):
    templates = [
        ("居住证申领", "户籍", "公安分局", "身份证,居住证明,照片", 7),
        ("户口迁入申请", "户籍", "公安分局", "身份证,户口簿,迁入证明", 10),
        ("出生登记办理", "户籍", "公安分局", "出生医学证明,父母身份证", 5),
        ("灵活就业社保补贴", "社保", "人社局", "身份证,社保缴费记录", 15),
        ("失业登记办理", "社保", "人社局", "身份证,解除劳动合同证明", 7),
        ("退休待遇资格确认", "社保", "人社局", "身份证,社保参保证明", 10),
        ("公租房申请", "住房", "住建局", "身份证,收入证明,住房证明", 15),
        ("住房补贴申请", "住房", "住建局", "身份证,劳动合同,租赁合同", 10),
        ("困难家庭救助申请", "民政", "民政局", "身份证,户口簿,收入证明", 10),
        ("临时救助申请", "民政", "民政局", "身份证,医疗或灾害证明", 7),
        ("学生资助申请", "教育", "教育局", "身份证,学籍证明,家庭情况证明", 12),
        ("医保异地就医备案", "医疗", "医保局", "身份证,医保卡,就医证明", 5),
    ]
    existing_names = {s.name for s in db.query(ServiceItem).all()}
    for idx, (name, category, dept, materials, days) in enumerate(templates):
        if name in existing_names:
            continue
        db.add(
            ServiceItem(
                name=name,
                category=category,
                department=dept,
                description=f"{name}线上申请与进度跟踪。",
                conditions=f"符合{category}办理条件。",
                materials=materials,
                processing_days=days,
                fee="免费",
                is_online=True,
                is_hot=idx < 4,
                status="enabled",
                created_at=datetime.utcnow() - timedelta(days=22 - idx),
            )
        )
    db.commit()


def ensure_announcements(db: Session):
    if db.query(Announcement).count() > 0:
        return
    rows = [
        ("系统上线通知", "居民政务服务系统已上线，支持在线申请与进度查询。", True),
        ("办理提醒", "请按事项指南准备申请材料，避免补正。", False),
        ("节假日通知", "节假日期间线上服务正常，线下窗口按安排值班。", False),
    ]
    for i, (title, content, is_top) in enumerate(rows):
        db.add(
            Announcement(
                title=title,
                content=content,
                is_top=is_top,
                created_at=datetime.utcnow() - timedelta(days=5 - i),
            )
        )
    db.commit()


def ensure_notifications(db: Session):
    admin = db.query(User).filter(User.username == "admin").first()
    resident = db.query(User).filter(User.username == "resident001").first()
    if not admin or not resident:
        return

    if db.query(Notification).filter(Notification.user_id == admin.id).count() == 0:
        db.add_all(
            [
                Notification(
                    user_id=admin.id,
                    title="系统通知",
                    content="请及时处理居民申请。",
                    is_read=False,
                    created_at=datetime.utcnow() - timedelta(hours=8),
                ),
                Notification(
                    user_id=admin.id,
                    title="公告提醒",
                    content="有新的公告需要审核发布。",
                    is_read=False,
                    created_at=datetime.utcnow() - timedelta(hours=4),
                ),
            ]
        )
    if db.query(Notification).filter(Notification.user_id == resident.id).count() == 0:
        db.add(
            Notification(
                user_id=resident.id,
                title="欢迎使用",
                content="请先完成实名认证后提交申请。",
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=2),
            )
        )
    db.commit()


def seed_data(db: Session):
    ensure_users(db)
    ensure_services(db)
    ensure_announcements(db)
    ensure_notifications(db)
