import json
def filter_messages(input_path='tdl-export.json', output_path='tdl-export-filtered.json'):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        messages = data.get("messages", [])
        filtered = []
        for msg in messages:
            text = msg.get("text")
            file = msg.get("file", "")
            # 跳过贴纸、表情包（.webp, .tgs, .webm）
            if isinstance(file, str) and file.lower().endswith((".webp", ".tgs", ".webm")):
                continue
            # 保留有文字、链接的消息
            if isinstance(text, str) and (text.strip() or "http" in text):
                filtered.append({"text": text.strip()})

        # 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"messages": filtered}, f, ensure_ascii=False, indent=2)
