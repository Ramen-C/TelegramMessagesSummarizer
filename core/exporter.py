# exporter.py
import subprocess
import time
from pathlib import Path
import json


def export_chat(chat_id, last_n=None, last_n_hours=None, progress_callback=None):
    """
    根据传入参数导出指定群聊的消息记录。支持通过回调函数报告进度。
    导出文件将保存到 ../json/tdl-export.json。
    """
    # --- 核心改动 1: 定义输出目录和文件路径 ---
    output_dir = Path('../json/')
    output_file = output_dir / 'tdl-export.json'

    # --- 核心改动 2: 确保输出目录存在，如果不存在则创建 ---
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取配置文件
    config_path = Path('../json/config.json')
    try:
        config = json.loads(config_path.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        raise FileNotFoundError(f"配置文件未找到或格式错误，请检查路径: {config_path}")

    proxy = config.get("proxy")

    # --- 核心改动 3: 在命令中加入 -o 参数指定输出文件 ---
    # 将 -o 参数放在命令前面，使其对所有导出类型都生效
    cmd_base = [
        config['tdl_path'], 'chat', 'export',
        '-c', str(chat_id),
        '-o', str(output_file)  # 将 Path 对象转换为字符串
    ]

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

    # 打印最终执行的命令，方便调试
    print("Executing command:", " ".join(cmd_base))

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

    # --- 核心改动 4: 更新最终的打印信息 ---
    print(f"消息导出完成，文件：{output_file}")