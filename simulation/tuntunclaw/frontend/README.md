# 前端说明

这里是 OpenClaw 的静态网页前端。

## 文件

- `index.html`
- `styles.css`
- `app.js`

## 使用方式

你可以直接在浏览器里打开 `index.html`，也可以通过仓库根目录的 `main.py`
启动一个本地 FastAPI 服务后访问网页。

直接打开静态 `index.html` 时默认进入 mock 预览模式，便于在没有 MuJoCo
环境的机器上检查界面。完整仿真并不使用该预览数据：通过仓库根目录的
`main.py` 启动 FastAPI 服务后，在顶部 `API` 按钮中设置后端基址即可连接
已经实现的 OpenClaw、VLM/SAM、GraspNet 和 MuJoCo 工作流。前端调用：

- `POST /api/command`
- `GET /api/session/:id`
- `GET /api/session/:id/events`

## 说明

- 页面采用深色背景和高亮文字。
- 命令输入支持 `Enter` 提交，`Shift+Enter` 换行。
- 已预置常用测试命令，方便快速试用。
