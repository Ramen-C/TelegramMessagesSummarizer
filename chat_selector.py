# chat_selector.py
import subprocess
import json

def list_chats():
    """
    列出所有聊天，要求用户选择一个群聊，并返回该群聊的 ID。
    """
    # 调用 tdl 列出所有聊天，使用 JSON 输出
    result = subprocess.run(['tdl', 'chat', 'ls', '-o', 'json'],
                            capture_output=True, text=True)
    data = json.loads(result.stdout)
    chats = data.get('result', [])
    if not chats:
        raise RuntimeError("未找到任何聊天。")
    # 显示聊天列表供用户选择
    print("可用的群聊列表：")
    for idx, chat in enumerate(chats, start=1):
        title = chat.get('Title', '<无标题>')
        chat_id = chat.get('Id', '')
        print(f"{idx}. {title} (ID: {chat_id})")
    # 用户输入选择序号
    choice = int(input("请输入要选择的群聊编号：")) - 1
    if choice < 0 or choice >= len(chats):
        raise ValueError("选择的编号超出范围。")
    selected_id = chats[choice]['Id']
    print(f"已选择群聊 ID：{selected_id}")
    return selected_id