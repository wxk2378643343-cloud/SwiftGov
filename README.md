# SwiftGov

SwiftGov 是一个政务业务流程演示项目，使用 Vue 前端、FastAPI 后端和 SQLite。业务需求和角色流程集中记录在 [需求文档](docs/requirements.md)。

| 路径 | 内容 |
| --- | --- |
| [secure/backend](secure/backend/README.md) | 修订版 API、依赖与数据库初始化 |
| [secure/frontend](secure/frontend/README.md) | 修订版 Web 界面、开发启动和 API 对接 |
| `vulnerable/` | 供防御性对照审阅的历史实现 |

## 本地使用

按修订版后端文档初始化本地数据库并启动 API，再按修订版前端文档启动界面。后端从运行目录打开 SQLite 文件，启动时应使用文档指定的工作目录。可通过 `JWT_SECRET` 和 `ALLOWED_ORIGINS` 配置修订版后端的签名密钥和允许的网页来源。

演示时使用独立的本地数据库和虚构业务数据。


后端入口为 `uvicorn app.main:app --reload --port 8001`，在 `secure/backend/` 中运行。前端在 `secure/frontend/` 中执行 `npm ci` 和 `npm run dev`，浏览器访问 Vite 输出的本地地址。
