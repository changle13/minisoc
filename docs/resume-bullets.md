# MiniSOC 简历包装

## 项目一句话

> 独立设计并实现轻量级安全运营与应急响应平台，完成日志采集、规则检测、告警去重、事件关联、自动封禁与审计闭环。

## 简历项目条目

### 版本 A：偏安全运营

**MiniSOC：轻量级安全运营与应急响应平台**  
独立开发 | Python / FastAPI / Vue 3 / PostgreSQL / Redis / Docker

- 设计并实现 Event / Alert / Incident 三层数据模型，完成从原始日志到安全事件工单的完整链路，支持告警详情回溯原始证据。
- 实现基于 5 分钟窗口的 SSH 暴力破解检测与告警去重，通过真实 SSH 密码爆破验证检测链路，检测延迟 X 秒，误报率 X%。
- 实现 Incident 关联逻辑，将同实体 10 分钟内的多条告警聚合为工单，降低重复告警噪音。
- 设计 HMAC 签名 + 时间戳 + IP 白名单 + 独立 iptables 链的自动响应 Agent，高危告警自动封禁攻击源 IP，响应时间 X 秒，动作写入双份审计。
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

简历上的数字必须来自你自己的测试，不要编。可以做：

- 检测延迟：从最后一条失败日志到 Alert 创建的时间
- 响应时间：从 Alert 创建到 iptables 规则生效的时间
- 误报率：正常 SSH 登录 + 正常流量跑 30 分钟，统计误报告警
- 检测覆盖率：已实现攻击场景 / 计划攻击场景

## 不要写

- “独立开发企业级 SIEM”
- “支持百万级日志”
- “零误报”
- 没做过的 ML、UEBA、威胁情报
- 没有测过的性能数字

写“轻量级 SOC”“MVP”“单机验证”，比夸大更可信。
