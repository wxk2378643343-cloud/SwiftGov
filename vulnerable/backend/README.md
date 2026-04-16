# Vulnerable Backend (FastAPI + SQLite)

## 说明
这是按需求文档实现的有漏洞版本后端，用于后续 `secure` 对照修复。

## 技术栈
- FastAPI
- SQLAlchemy
- SQLite

## 快速启动
```bash
cd vulnerable/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 模拟数据
- 默认最小数据：仅 `admin + resident001` 两个账号，3个事项，3条公告，少量消息。
- 居民可继续通过注册功能新增账号。

## 默认账号
- `admin / admin123`
- `resident001 / 123456`

## 已覆盖能力（MVP）
- 登录鉴权、角色权限
- 双角色：`resident` / `admin`
- 权限点模型（查看/编辑/提交/审批）与接口鉴权
- 个人资料修改与密码修改
- 用户管理、角色与部门基础接口
- 事项管理、申请管理、受理审批流转
- 公告管理、消息通知、评价反馈
- 统计概览、操作日志
- ECharts 数据接口：趋势、状态分布、事项排行

## 已知漏洞（故意保留）
- 明文密码存储
- Token 直接使用用户 ID，可伪造
- CORS 全开放
- 缺少严格输入校验与限流
- 材料上传仅做元数据模拟，无安全检查
