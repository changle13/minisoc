import time

import paramiko

HOST = "192.168.65.20"
PORT = 22
USERNAME = "victim"
PASSWORDS = [f"wrong-password-{index}" for index in range(1, 7)]

for index, password in enumerate(PASSWORDS, start=1):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=HOST,
            port=PORT,
            username=USERNAME,
            password=password,
            timeout=5,
            banner_timeout=5,
            auth_timeout=5,
            allow_agent=False,
            look_for_keys=False,
        )
        print(f"[{index}] unexpected success")
    except paramiko.AuthenticationException:
        print(f"[{index}] authentication failed")
    except Exception as exc:
        print(f"[{index}] error: {exc}")
    finally:
        client.close()
    time.sleep(0.3)
