# forwarder.py
import subprocess
import json
from pathlib import Path


def forward_summary(chat_id, summary, progress_callback=None):
    """
    使用 tdl up 将摘要文件 summary.txt 上传到指定群聊。支持进度回调。
    """
    config_path = Path('../settings/config.json')
    config = json.loads(config_path.read_text())
    proxy = config.get("proxy")

    with open('../export/summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)

    # 如果 chat_id 为空或不是有效数字, tdl 会默认发到收藏夹
    cmd = [config["tdl_path"], 'up', '-p', '../export/summary.txt']
    if str(chat_id).strip():
        cmd.extend(['-c', str(chat_id)])

    if proxy:
        cmd.extend(['--proxy', proxy])

    if progress_callback:
        progress_callback("status_forwarding", 80)

    print("执行命令：", " ".join(cmd))

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                               errors='replace')

    while True:
        line = process.stdout.readline()
        if not line:
            break
        if progress_callback:
            progress_callback("status_forwarding", -1)

    process.wait()

    if process.returncode != 0:
        raise Exception(f"Forwarding failed. tdl exit code: {process.returncode}")

    if progress_callback:
        progress_callback("status_forwarding", 100)

    print("摘要文件已上传到群聊。")