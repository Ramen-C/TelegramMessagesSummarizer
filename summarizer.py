# summarizer.py
import json
from openai import OpenAI

def summarize_chat():
    """
    使用 DeepSeek API 对导出的聊天记录进行分析，并返回 Markdown 格式的摘要字符串。
    """
    # 读取导出的 JSON 消息
    with open('tdl-export.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 假设 JSON 中消息内容字段为 'Text'
    messages = [msg.get('Text', '') for msg in data.get('result', []) if msg.get('Text')]
    chat_text = "\n".join(messages)

    # DeepSeek 客户端初始化
    DEEPSEEK_API_KEY = 'sk-80f4be0c573f49dfb31558c774ccf1f0'
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    # 构造提示词（system + user）
    system_prompt = "你是一个擅长提取关键信息的聊天摘要专家。"
    user_prompt = (
        "请分析以下对话内容：\n"
        "1. 识别对话中的 URL 链接，并根据上下文推测链接指向的内容。\n"
        "2. 提取讨论的核心要点：如果讨论的是活动，请标注活动的时间和地点；"
        "如果讨论的是游戏，请标注游戏名称和主要观点。\n"
        "3. 输出一个结构化摘要，使用以下 Markdown 格式：**粗体**、__斜体__、~~删除线~~、```等宽```、||剧透|| 等。\n"
        "对话内容如下：\n"
        f"{chat_text}"
    )

    # 调用 DeepSeek (deepseek-chat 模型)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False
    )
    summary = response.choices[0].message.content
    print("=== 聊天摘要 ===")
    print(summary)
    return summary