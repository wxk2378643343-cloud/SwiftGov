# Secure Backend (FastAPI + SQLite)

## 说明
这是 `secure` 版本后端，基于 `vulnerable` 版本加固而来。

## 技术栈
- FastAPI
- SQLAlchemy
- SQLite

## 快速启动
```bash
cd secure/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## 模拟数据
- 默认最小数据：仅 `admin + resident001` 两个账号，3个事项，3条公告，少量消息。
- 居民可继续通过注册功能新增账号。

## 默认账号
- `admin / admin123`
- `resident001 / 123456`

## 已覆盖能力（MVP）
- JWT 登录鉴权、角色权限
- 双角色：`resident` / `admin`
- 权限点模型（查看/编辑/提交/审批）与接口鉴权
- 个人资料修改与密码修改
- 用户管理、角色与部门基础接口
- 事项管理、申请管理、受理审批流转
- 公告管理、消息通知、评价反馈
- 统计概览、操作日志
- ECharts 数据接口：趋势、状态分布、事项排行

## 安全加固点
- 密码哈希存储（bcrypt）
- JWT 签名令牌（含过期）
- 登录失败限流（基础版）
- CORS 白名单配置（可通过 `ALLOWED_ORIGINS` 覆盖）
- 注册/改密密码强度校验（至少8位且含字母+数字）
