# translations.py

TRANSLATIONS = {
    "zh": {
        "window_title": "Telegram AI 群聊助手 (Deepseek Reasoner 专用版)",
        "load_chats": "刷新群聊列表",
        "load_chats_success": "已成功加载 {} 个群聊",
        "load_chats_fail": "加载群聊列表失败: {}",
        "load_chats_from_cache": "已从缓存加载 {} 个群聊",
        "export_settings": "导出设置",
        "recent_n_msgs": "最近 N 条消息",
        "recent_n_hours": "最近 N 小时",
        "n_equals": "N =",
        "no_chat_selected": "未选择群聊",
        "current_chat": "当前群组: {}",
        "forward_settings": "转发设置",
        "forward_to_target": "转发到指定目标 (填Chat ID)",
        "forward_default": "默认转发到“收藏夹”",
        "start_summary": "开始总结",
        "settings": "⚙️ 设置",
        "chat_list": "群聊列表 (请点击选择)",
        "summary_results": "摘要结果",
        "core_wordcloud": "核心词云",
        "error": "错误",
        "success": "成功",
        "warning": "警告",
        "info": "信息",
        "processing": "处理中",
        "invalid_selection": "请先在右侧列表中选择一个群聊。",
        "invalid_n": "N 必须为正整数。",
        "export_and_analyze": "正在导出和分析消息，请稍候...",
        "no_valid_messages": "过滤后没有找到有效的文本消息。",
        "forward_target_empty": "您已勾选自选目标，请填写有效的 Chat ID。",
        "summary_finished_and_forwarded": "摘要已在界面显示，并成功转发！",
        "processing_failed": "处理失败: {}",
        "settings_title": "设置",
        "tdl_path": "TDL 路径:",
        "proxy_address": "代理地址:",
        "api_key": "DeepSeek API Key:",
        "language": "语言:",
        "generate_wordcloud": "生成词云",
        "save": "保存",
        "cancel": "取消",
        "settings_saved": "设置已保存！重启应用后，语言设置将完全生效。",
        "status_loading_chats": "正在加载群聊列表...",
        "status_exporting": "正在导出消息...",
        "status_filtering": "正在过滤消息...",
        "status_summarizing": "正在调用 AI 进行总结...",
        "status_generating_wordcloud": "正在生成词云...",
        "status_forwarding": "正在转发摘要...",
        "status_done": "任务完成！",
        "status_ready": "准备就绪",
        "status_error": "出现错误",
        "reading_terminal_output": "正在读取 tdl 输出..."
    },
    "en": {
        "window_title": "Telegram AI Chat Assistant (for Deepseek Reasoner)",
        "load_chats": "Refresh Chat List",
        "load_chats_success": "Successfully loaded {} chats",
        "load_chats_fail": "Failed to load chat list: {}",
        "load_chats_from_cache": "Loaded {} chats from cache",
        "export_settings": "Export Settings",
        "recent_n_msgs": "Last N Messages",
        "recent_n_hours": "Last N Hours",
        "n_equals": "N =",
        "no_chat_selected": "No chat selected",
        "current_chat": "Current Chat: {}",
        "forward_settings": "Forwarding Settings",
        "forward_to_target": "Forward to a specific target (Chat ID)",
        "forward_default": "Default: forward to 'Saved Messages'",
        "start_summary": "Start Summarizing",
        "settings": "⚙️ Settings",
        "chat_list": "Chat List (Click to select)",
        "summary_results": "Summary Results",
        "core_wordcloud": "Core Word Cloud",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info",
        "processing": "Processing",
        "invalid_selection": "Please select a chat from the list on the right.",
        "invalid_n": "N must be a positive integer.",
        "export_and_analyze": "Exporting and analyzing messages, please wait...",
        "no_valid_messages": "No valid text messages found after filtering.",
        "forward_target_empty": "You have checked 'specific target', please enter a valid Chat ID.",
        "summary_finished_and_forwarded": "Summary displayed and forwarded successfully!",
        "processing_failed": "Processing failed: {}",
        "settings_title": "Settings",
        "tdl_path": "TDL Path:",
        "proxy_address": "Proxy Address:",
        "api_key": "DeepSeek API Key:",
        "language": "Language:",
        "generate_wordcloud": "Generate Word Cloud",
        "save": "Save",
        "cancel": "Cancel",
        "settings_saved": "Settings saved! Language changes will take full effect after restarting the application.",
        "status_loading_chats": "Loading chat list...",
        "status_exporting": "Exporting messages...",
        "status_filtering": "Filtering messages...",
        "status_summarizing": "Summarizing with AI...",
        "status_generating_wordcloud": "Generating word cloud...",
        "status_forwarding": "Forwarding summary...",
        "status_done": "Task complete!",
        "status_ready": "Ready",
        "status_error": "An error occurred",
        "reading_terminal_output": "Reading tdl output..."
    }
}

# --- 全局翻译函数 ---
_current_language = "zh"

def set_language(lang_code):
    global _current_language
    if lang_code in TRANSLATIONS:
        _current_language = lang_code
    else:
        _current_language = "en" # Fallback to English

def get_string(key):
    return TRANSLATIONS.get(_current_language, TRANSLATIONS["en"]).get(key, key)

# --- 为了方便使用，创建一个别名 ---
_ = get_string