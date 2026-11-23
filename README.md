# SwiftGov 政务服务流程系统

![Vue 3](https://img.shields.io/badge/Vue%203-2563EB?style=flat-square)
![Vite](https://img.shields.io/badge/Vite-0F766E?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-334155?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-B45309?style=flat-square)

## 📌 项目简介

面向居民提交事项申请、管理端受理审批和公告管理的政务流程演示。

本仓库供**网络安全学习**使用。 `vulnerable/` 是有漏洞的历史对照版本，`secure/` 是针对课程示例做过修复的版本。可以对照两套源码，理解防护措施和代码变更。

## 🏗️ 系统架构

- 两个版本分别包含 Vue 前端、FastAPI 后端和各自的本地数据库。
- 前端负责用户交互，后端提供业务 API，SQLite 保存各版本的演示数据。

## 📁 项目结构

| 路径 | 用途 |
| --- | --- |
| [`secure/frontend`](secure/frontend) | 修订版 Web 界面 |
| [`secure/backend`](secure/backend) | 修订版 API 与数据库逻辑 |
| [`vulnerable`](vulnerable) | 用于防御性对照的历史源码 |

## 🚀 如何启动

本地演示使用修订版。先启动后端，再在各自的前端目录运行 `npm ci` 和 `npm run dev`。具体环境和后端命令见[后端说明](secure/backend/README.md)和[前端说明](secure/frontend/README.md)。后端在自己的运行目录中打开 SQLite 数据库。

| 入口 | 默认地址 |
| --- | --- |
| API | `http://localhost:8001` |
| Web | `http://localhost:5174` |

演示数据和数据库按版本分开保存。相关资料见[需求文档](docs/requirements.md)。

---
## ✨ 安全对照学习亮点与合规说明

1. **双版本源码对照学习法**：仓库并列维护 `vulnerable/`（历史漏洞对照版）与 `secure/`（安全加固修订版），围绕政务事项申请、多级审批与公告消息场景，便于通过代码对比直观掌握角色越权防护、认证鉴权与输入校验等核心 Web 安全实践。
2. **合规与使用声明**：`vulnerable/` 仅用于本地网络安全学习与防御对照，**严禁部署至公网环境**；日常演示与运行请统一使用 `secure/`。

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源，详见根目录 [LICENSE](LICENSE) 文件。
