# MiniSOC 简历包装

## 最终推荐版

**2026.11　MiniSOC：轻量级安全运营与应急响应平台　独立开发 / 安全开发**

**技术栈：** Python / FastAPI / Vue 3 / PostgreSQL / Redis / Docker / Linux / iptables

**项目描述：**
独立设计并实现轻量级 SOC 平台，完成日志采集、规则检测、告警去重、事件工单、JWT/RBAC、自动封禁与审计闭环；通过真实 SSH 爆破验证检测与响应链路。

**主要工作：**

1. **日志接入与检测：** 自研 Python Agent 读取 `auth.log`，支持 offset 断点续传、批量上报、失败重试和至少一次投递；实现 API Key 接入、Event 标准化与 JSONB 原始日志留存；基于 5 分钟窗口实现 SSH 爆破检测，按“规则 + 实体 + 时间桶”去重并更新 `count/last_seen`。
2. **告警与事件模型：** 设计 Event / Alert / Incident 三层模型及 `alert_events`、`incident_alerts` 关联表；实现告警列表/详情 API，支持 severity/status 筛选和分页，并通过关联表回溯原始 Event 证据；实现同实体 10 分钟内多条告警自动聚合为 Incident。
3. **认证与权限：** 实现 API Key（Agent）与 JWT（用户）双认证体系，密码使用 bcrypt 哈希；基于 RBAC 实现 viewer / analyst / admin 权限控制，区分 401 未认证与 403 无权限。
4. **自动响应与审计：** 设计 HMAC-SHA256 + 时间戳防重放的响应 Agent，加入 IP 白名单、独立 iptables 链、dry-run 和双份审计；高危 SSH 爆破告警自动封禁来源 IP，响应结果写入 SOC `response_actions` 表。
5. **前端与部署：** 使用 Vue 3 + Element Plus 实现登录、告警中心、告警详情、事件工单和响应记录页面；实现路由守卫、JWT 请求注入和 Vite 代理；使用 Docker Compose 部署 FastAPI、PostgreSQL、Redis。

**项目成果：**

- 真实 SSH 爆破验证：从 Windows 对 Victim 发起 6 次失败登录，触发 1 条高危 Alert（`count=6`），最后一条失败日志到告警创建约 **8.2 秒**（本地单机靶场）。
- 自动响应：告警创建到响应审计落库约 **0.017-0.038 秒**，成功在 Victim 的 `MINISOC_BLOCK` 链写入/删除 DROP 规则。
- 形成“采集 → 检测 → 告警 → 事件 → 响应 → 审计”的可复用闭环，项目已开源：https://github.com/changle13/minisoc

## 一页简历精简版

**MiniSOC 轻量级安全运营与应急响应平台　|　独立开发**

- 独立完成 FastAPI + Vue 3 + PostgreSQL + Redis + Docker 的 SOC 平台，实现日志接入、SSH 爆破检测、告警去重、事件工单、JWT/RBAC、自动封禁和审计闭环。
- 自研日志 Agent 支持 offset 断点续传、批量上报与失败重试；设计 Event/Alert/Incident 三层模型和关联表，告警详情可回溯原始证据。
- 设计 HMAC + 时间戳 + IP 白名单的响应 Agent，高危 SSH 爆破自动封禁来源 IP，响应审计约 0.017-0.038 秒；真实爆破验证告警创建约 8.2 秒。
- GitHub：https://github.com/changle13/minisoc

## 项目一句话

> 独立设计并实现轻量级安全运营与应急响应平台，完成日志采集、规则检测、告警去重、事件关联、自动封禁与审计闭环。

## 简历项目条目

### 版本 A：偏安全运营

**MiniSOC：轻量级安全运营与应急响应平台**  
独立开发 | Python / FastAPI / Vue 3 / PostgreSQL / Redis / Docker

- 设计并实现 Event / Alert / Incident 三层数据模型，完成从原始日志到安全事件工单的完整链路，支持告警详情回溯原始证据。
- 实现基于 5 分钟窗口的 SSH 暴力破解检测与告警去重，通过真实 SSH 密码爆破验证检测链路，最后一条失败日志到告警创建约 8.2 秒（本地单机靶场）。
- 实现 Incident 关联逻辑，将同实体 10 分钟内的多条告警聚合为工单，降低重复告警噪音。
- 设计 HMAC 签名 + 时间戳 + IP 白名单 + 独立 iptables 链的自动响应 Agent，高危告警自动封禁攻击源 IP，告警创建到响应审计落库约 0.017-0.038 秒，动作写入双份审计。
- 实现 API Key（Agent）与 JWT + RBAC（用户）双层认证，使用 bcrypt 存储密码，保护告警、事件和响应接口。

### 版本 B：偏安全开发

**MiniSOC：轻量级安全运营平台**  
独立开发 | FastAPI / Vue 3 / PostgreSQL / Redis / Docker / Linux

- 独立完成后端、日志 Agent、响应 Agent 和 Vue 前端，使用 Docker Compose 一键部署 API、PostgreSQL、Redis。
- 自研日志 Agent，支持 offset 断点续传、批量上报、失败重试和至少一次投递语义。
- 实现 YAML/规则化检测链路与告警去重，支持 ATT&CK 映射、告警详情证据回溯。
- 实现 JWT + RBAC 和 API Key 双认证体系，完成 viewer / analyst / admin 权限控制。
- 完成真实攻击验证：从 Windows 对 Victim 发起 SSH 爆破，SOC 成功产生告警并自动封禁攻击 IP。

## 面试讲述顺序

1. **为什么做**：想理解 SOC 的完整闭环，而不是只部署 Wazuh/ELK
2. **怎么设计**：Event / Alert / Incident 三层模型 + 检测 + 响应
3. **怎么验证**：真实 SSH 爆破，6 次失败触发告警，自动封禁并审计
4. **怎么保证安全**：API Key/JWT 分离、HMAC、白名单、dry-run、审计
5. **有什么取舍**：PostgreSQL 而不是 ELK；同步 MVP；未来异步化

## 指标填写说明

简历上的数字必须来自你自己的测试，不要编。当前已经实测：

- 真实 SSH 爆破：最后一条失败日志到 Alert 创建约 8.2 秒
- 自动响应：Alert 创建到 `response_actions` 审计落库约 0.017-0.038 秒
- 测试环境：本地单机靶场，非生产压测数据

还需要补测：

- 误报率：正常 SSH 登录 + 正常流量跑 30 分钟，统计误报告警
- 检测覆盖率：已实现攻击场景 / 计划攻击场景

## 不要写

- “独立开发企业级 SIEM”
- “支持百万级日志”
- “零误报”
- 没做过的 ML、UEBA、威胁情报
- 没有测过的性能数字

写“轻量级 SOC”“MVP”“单机验证”，比夸大更可信。
