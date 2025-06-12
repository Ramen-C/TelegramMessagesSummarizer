# exporter.py
import subprocess
import time
from pathlib import Path
import json

def export_chat(chat_id, last_n=None, last_n_hours=None):
    """
    根据传入参数导出指定群聊的消息记录。支持最新 N 条或最近 N 小时内的消息。
    默认输出文件为 tdl-export.json。
    """

    # 读取配置
    config_path = Path('config.json')
    config = json.loads(config_path.read_text())
    proxy = config.get("proxy")  # 可为空

    if last_n is not None:
        cmd = [config['tdl_path'], 'chat', 'export', '-c', str(chat_id), '-T', 'last', '-i', str(last_n),'--all','--with-content','--raw']
        if proxy:
            cmd.extend(['--proxy', proxy])
    elif last_n_hours is not None:
        now = int(time.time())
        since = now - int(last_n_hours * 3600)
        cmd = [config['tdl_path'], 'chat', 'export', '-c', str(chat_id), '-T', 'time', '-i', f"{since},{now}",'--all','--with-content']
        if proxy:
            cmd.extend(['--proxy', proxy])
    else:
        raise ValueError("必须指定导出的消息数量或小时数。")

    subprocess.run(cmd)
    print("消息导出完成，文件：tdl-export.json")