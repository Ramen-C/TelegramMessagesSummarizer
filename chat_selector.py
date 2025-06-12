# chat_selector.py

import subprocess
import json
from pathlib import Path


def list_chats():
    """
    调用 `tdl chat ls` 命令，解析其纯文本输出，并返回一个包含群聊信息的字典列表。
    能够正确处理 VisibleName 中包含空格的情况。
    """
    # 读取配置
    config_path = Path('config.json')
    try:
        config = json.loads(config_path.read_text())
    except FileNotFoundError:
        # 如果没有配置文件，使用默认值
        config = {"tdl_path": "tdl", "proxy": None}

    proxy = config.get("proxy")

    # --- 核心改动：不再使用 -o json ---
    cmd = [config['tdl_path'], 'chat', 'ls']
    if proxy:
        cmd.extend(['--proxy', proxy])

    # 调用 tdl 并捕获输出
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # 获取标准输出并按行分割
    output_lines = result.stdout.strip().split('\n')

    # 如果输出少于2行（只有标题行或为空），则返回空列表
    if len(output_lines) < 2:
        return []

    parsed_chats = []
    # 从第二行开始遍历，跳过标题行
    for line in output_lines[1:]:
        parts = line.split()
        if len(parts) < 4:  # 每行至少要有 ID, Type, Name, Username 四个部分
            continue

        # 解析每一部分
        chat_id = parts[0]
        chat_type = parts[1]

        # 倒数第二个是 Username，倒数第一个是 Topics (我们不需要)
        chat_username = parts[-2]

        # 中间的所有部分都属于 VisibleName
        chat_visible_name = " ".join(parts[2:-2])

        # 组装成字典
        parsed_chats.append({
            'id': chat_id,
            'type': chat_type,
            'visible_name': chat_visible_name,
            'username': chat_username
        })

    return parsed_chats