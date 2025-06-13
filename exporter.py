# exporter.py
import subprocess
import time
from pathlib import Path
import json


def export_chat(chat_id, last_n=None, last_n_hours=None, progress_callback=None):
    """
    根据传入参数导出指定群聊的消息记录。支持通过回调函数报告进度。
    """
    config_path = Path('config.json')
    config = json.loads(config_path.read_text())
    proxy = config.get("proxy")

    cmd_base = [config['tdl_path'], 'chat', 'export', '-c', str(chat_id)]

    if last_n is not None:
        cmd_base.extend(['-T', 'last', '-i', str(last_n), '--all', '--with-content', '--raw'])
    elif last_n_hours is not None:
        now = int(time.time())
        since = now - int(last_n_hours * 3600)
        cmd_base.extend(['-T', 'time', '-i', f"{since},{now}", '--all', '--with-content', '--raw'])
    else:
        raise ValueError("必须指定导出的消息数量或小时数。")

    if proxy:
        cmd_base.extend(['--proxy', proxy])

    if progress_callback:
        progress_callback("status_exporting", 20)

    process = subprocess.Popen(cmd_base, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                               errors='replace')

    while True:
        line = process.stdout.readline()
        if not line:
            break
        # tdl的导出进度比较难解析，这里只更新状态文本
        if progress_callback:
            progress_callback("status_exporting", -1)  # 不确定进度

    process.wait()

    if process.returncode != 0:
        raise Exception(f"Export failed. tdl exit code: {process.returncode}")

    if progress_callback:
        progress_callback("status_exporting", 100)

    print("消息导出完成，文件：tdl-export.json")