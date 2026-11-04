# Lab Scripts

本目录只允许在 MiniSOC 隔离靶场中使用。

## 脚本

### `attack-scripts/send_fake_bruteforce.py`

向 SOC 接入 API 发送 6 条合成 SSH 失败事件，来源 IP 固定为 `192.168.65.99`。  
脚本会自动读取 `deploy/.env` 中的 `API_KEY`。

用途：

- 验证“检测 → 告警 → 自动响应 → 审计”闭环
- 不封禁演示主机或 SOC

在 SOC 上运行：

```bash
cd ~/minisoc
python3 lab/attack-scripts/send_fake_bruteforce.py
```

### `attack-scripts/send_response_action.py`

直接向 Victim 响应 Agent 发送带 HMAC 签名的 block/unblock 请求。  
脚本会自动读取 `deploy/.env` 中的 `RESPONSE_AGENT_SECRET`。

```bash
python3 lab/attack-scripts/send_response_action.py block 192.168.65.99
python3 lab/attack-scripts/send_response_action.py unblock 192.168.65.99
```

### `attack-scripts/ssh_bruteforce_sim.py`

使用 Paramiko 对 Victim 发起 6 次错误 SSH 密码尝试。

依赖：

```bash
pip install paramiko
```

仅用于授权靶场，禁止对未授权目标使用。
