# MiniSOC

轻量级安全运营与应急响应平台（MiniSOC）。

## 当前进度

- [x] Ubuntu Server 22.04 VM + SSH
- [x] Docker + Docker Compose
- [x] FastAPI + PostgreSQL + Redis 基础骨架
- [ ] 日志采集与标准化
- [ ] 检测引擎与告警关联
- [ ] 事件工单与自动响应
- [ ] 前端仪表盘
- [ ] 攻击场景验证与报告

## 快速启动

```bash
cd deploy
docker compose up -d --build
curl http://localhost:8000/health
```

## 目录结构

```text
backend/          FastAPI 后端
frontend/         Vue 3 前端
agent/            日志采集 Agent
response-agent/   响应 Agent
lab/              靶场与攻击脚本
deploy/           Docker Compose 部署文件
docs/             架构、威胁模型、攻击复现文档
```

## 安全说明

所有扫描、攻击和自动响应仅允许在本项目的隔离靶场中执行，禁止对未授权目标使用。
