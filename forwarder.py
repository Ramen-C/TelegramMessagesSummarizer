# forwarder.py
import subprocess
import json

def forward_summary(chat_id, summary):
    """
    使用 tdl up 将摘要文件 summary.txt 上传到指定群聊。
    """
    # 保存摘要内容到文件
    with open('summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)

    # 使用 tdl up 上传文件
    cmd = ['tdl', 'up', '-p', 'summary.txt', '-c', str(chat_id)]
    print("执行命令：", " ".join(cmd))
    subprocess.run(cmd)
    print("摘要文件已上传到群聊。")