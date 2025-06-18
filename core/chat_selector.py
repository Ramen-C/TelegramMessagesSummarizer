# chat_selector.py

import subprocess
import json
from pathlib import Path

def list_chats(progress_callback=None):
    """
    调用 `tdl chat ls -o settings` 命令，直接解析其 JSON 输出。
    此版本更简洁、更健壮，直接处理完整的 stdout。
    """
    config_path = Path('../settings/config.json')
    try:
        config = json.loads(config_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果没有或损坏，使用默认值
        config = {"tdl_path": "tdl", "proxy": None}

    proxy = config.get("proxy")

    cmd = [config['tdl_path'], 'chat', 'ls', '-o', 'settings']
    if proxy:
        cmd.extend(['--proxy', proxy])

    if progress_callback:
        progress_callback("status_loading_chats", 10) # 标记任务开始

    try:
        # --- 核心改动：使用更简洁、可靠的 subprocess.run ---
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,  # 如果命令失败（返回非0），则自动抛出 CalledProcessError
            encoding='utf-8'
        )

        # 直接解析标准输出，因为 tdl 在 -o settings 模式下输出的是纯净的 JSON
        json_data = json.loads(result.stdout)

        if progress_callback:
            progress_callback("status_loading_chats", 100) # 标记任务完成

        return json_data

    except subprocess.CalledProcessError as e:
        # 当 tdl 命令执行失败时捕获错误
        error_output = e.stderr or e.stdout
        raise Exception(f"tdl 'chat ls' command failed:\n{error_output}")
    except json.JSONDecodeError:
        # 当 tdl 输出的不是有效的 JSON 时捕获错误
        raise Exception(f"Failed to parse JSON from tdl. Output was:\n{result.stdout}")
    except FileNotFoundError:
        # 当 tdl 命令本身找不到时捕获错误
        raise Exception(f"Command '{config['tdl_path']}' not found. Please check 'tdl_path' in settings.settings.")