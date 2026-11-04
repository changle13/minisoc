# MiniSOC 演示脚本

目标：3-5 分钟内讲清“采集 → 检测 → 告警 → 事件工单 → 自动响应 → 审计”。

## 演示前检查

```bash
cd ~/minisoc/deploy
docker compose ps
curl -sS http://localhost:8000/health
```

前端：

```text
http://192.168.65.10:5173
admin / admin_dev_password
```

Victim：

```text
192.168.65.20
```

响应 Agent：

```bash
curl -sS http://192.168.65.20:9000/health
```

应返回：

```json
{"status": "ok", "dry_run": false}
```

## 1. 架构介绍（30 秒）

展示 `docs/architecture.md` 的图：

- Victim 产生 auth.log
- Agent 上报到 SOC
- SOC 检测、告警、关联
- 高危告警调用 Victim 响应 Agent
- 响应 Agent 执行 iptables 并写审计

## 2. 告警中心（40 秒）

登录后进入「告警中心」：

- 展示告警列表
- 筛选 `high`
- 点击 Alert 3：真实 SSH 爆破，`entity=192.168.65.1`，`count=6`
- 进入详情，展示 6 条原始 Event 证据

讲解重点：

> 列表返回摘要，详情通过 `alert_events` 回溯原始证据。

## 3. 事件工单（30 秒）

进入「事件工单」：

- 展示 Incident 1
- 点开详情
- 展示关联的 2 条 Alert

讲解重点：

> 同一实体 10 分钟内多条告警合并成案件，减少单条告警噪音。

## 4. 响应记录（30 秒）

进入「响应记录」：

- 展示自动封禁记录
- `Alert ID=4`
- `action=block`
- `target_ip=192.168.65.99`
- `status=blocked`
- 详情中包含 iptables 规则

讲解重点：

> SOC 决策，Victim 执行；响应结果进入 `response_actions` 审计表。

## 5. 现场触发一次自动响应（60 秒）

使用测试 IP `192.168.65.99`，避免封禁演示主机。

在 SOC 上执行：

```bash
cd ~/minisoc
python3 lab/attack-scripts/send_fake_bruteforce.py
```

脚本会向 SOC 发送 6 条失败登录事件。

预期：

1. 前端刷新告警中心，出现新的高危告警
2. 响应记录新增一条 `block 192.168.65.99`
3. SOC 自动调用 Victim 响应 Agent
4. Victim 执行 iptables，封禁 `.99`

展示 Victim 本地审计：

```bash
tail -n 5 /var/log/minisoc-response.jsonl
```

## 6. 解封测试 IP（20 秒）

在 SOC 上执行：

```bash
cd ~/minisoc
python3 lab/attack-scripts/send_response_action.py unblock 192.168.65.99
```

预期返回：

```json
{"ok": true, "result": "unblocked", "rules": ["-N MINISOC_BLOCK"]}
```

讲解重点：

> 测试 IP 解封后，不影响真实攻击证据和告警记录。

## 7. 安全设计总结（30 秒）

- Agent 用 API Key，用户用 JWT
- 密码 bcrypt 哈希
- RBAC 最小权限
- 响应 Agent 用 HMAC + 时间戳 + 白名单
- 响应默认 dry-run，执行动作双份审计
- 当前同步检测/响应是 MVP 取舍，生产应改异步

## 8. 结尾一句话

> 这个项目不是“装了一个安全产品”，而是自己实现并验证了一条可追溯、可响应、可审计的安全运营闭环。
