# exporter.py
import subprocess
import time

def export_chat(chat_id):
    """
    根据用户输入导出指定群聊的消息记录。支持最新 N 条或最近 N 小时内的消息。
    默认输出文件为 tdl-export.json。
    """
    mode = input("请选择导出方式（输入 'last' 导出最新N条，输入 'time' 导出最近N小时）：").strip().lower()
    if mode == 'last':
        count = input("请输入要导出的消息条数 N：").strip()
        cmd = ['tdl', 'chat', 'export', '-c', str(chat_id), '-T', 'last', '-i', count]
    elif mode == 'time':
        hours = float(input("请输入要导出的时间跨度（小时）："))
        now = int(time.time())
        since = now - int(hours * 3600)
        # 使用时间戳范围导出
        cmd = ['tdl', 'chat', 'export', '-c', str(chat_id), '-T', 'time', '-i', f"{since},{now}"]
    else:
        raise ValueError("无效的导出方式。请输入 'last' 或 'time'。")
    print("执行命令：", " ".join(cmd))
    subprocess.run(cmd)
    print("消息导出完成，文件：tdl-export.json")