import json
import subprocess
from pathlib import Path


def list_chats():
    """
    列出所有聊天，要求用户选择一个群聊，并返回该群聊的 ID。
    """

    # 读取配置
    config_path = Path('config.json')
    config = json.loads(config_path.read_text())
    proxy = config.get("proxy")  # 可为空

    cmd = [config['tdl_path'], 'chat', 'ls', '-o', 'json']
    if proxy:
        cmd.extend(['--proxy', proxy])

    # 调用 tdl
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data