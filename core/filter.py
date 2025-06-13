# filter.py

import json

def filter_and_format_messages(input_path='../json/tdl-export.json'): # <--- 在这里修改默认路径
    """
    读取原始导出文件，进行过滤、匿名化和格式化，并返回一个倒序的字符串列表。

    优化点:
    1.  **倒序处理**: 将消息列表反转，让最新的消息出现在最前面。
    2.  **内存处理**: 不再生成中间JSON文件，直接返回一个Python列表。
    3.  **格式简洁**: 返回的列表中，每项都是 "User A: [内容]" 格式的字符串。
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"警告: {input_path} 未找到或格式无效，将返回空列表。")
        return []

    messages = data.get("messages", [])
    if not messages:
        return []

    # --- 核心改动 1: 将聊天记录倒序 ---
    messages.reverse()

    user_map = {}
    user_counter = 0
    formatted_list = []

    for msg in messages:
        raw_data = msg.get('raw')
        if not isinstance(raw_data, dict):
            continue

        # 精确过滤贴纸
        media = raw_data.get('Media')
        if isinstance(media, dict):
            doc = media.get('Document')
            if isinstance(doc, dict) and doc.get('MimeType', '').lower() in ['video/webm', 'application/x-tgsticker']:
                continue

        # 统一提取文本
        text_content = raw_data.get('Message', '').strip()
        if not text_content:
            continue

        # 匿名化用户ID
        anonymized_id = "系统/频道"
        from_id_obj = raw_data.get('FromID')
        if isinstance(from_id_obj, dict):
            user_id = from_id_obj.get('UserID')
            if user_id:
                if user_id not in user_map:
                    user_map[user_id] = f"User {chr(ord('A') + user_counter % 26)}"
                    user_counter += 1
                anonymized_id = user_map[user_id]

        # --- 核心改动 2: 直接添加格式化后的字符串到列表 ---
        formatted_list.append(f"{anonymized_id}: {text_content}")

    # --- 核心改动 3: 返回处理好的列表，而不是写入文件 ---
    return formatted_list