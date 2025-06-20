from pathlib import Path
from tkinter import messagebox
import json

CONFIG_FILE = Path("../settings/config.json")

def load_config():
    """加载配置文件，如果文件不存在或损坏，则创建并使用默认文件。"""
    default_config = {
        "tdl_path": "tdl",
        "proxy": "",
        "api": "sk-...",
        "language": "zh",
        "generate_wordcloud": True
    }
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 确保所有键都存在
            for key, value in default_config.items():
                config.setdefault(key, value)
            return config
    except (json.JSONDecodeError, TypeError):
        messagebox.showerror("Config Error", "settings.settings is corrupted. Using default settings.")
        return default_config


def save_config(config_data):
    """保存配置到文件。"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
