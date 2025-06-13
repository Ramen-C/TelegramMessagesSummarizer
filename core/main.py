# main.py

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import json
from pathlib import Path
import threading
import queue

# --- NEW: 项目模块导入 ---
from translations import set_language, _
import chat_selector
import exporter
import summarizer
import forwarder
from filter import filter_and_format_messages
from visualizer import generate_wordcloud

CONFIG_FILE = Path("../json/config.json")
CHATS_CACHE_FILE = Path("../json/chats.json")


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
        messagebox.showerror("Config Error", "config.json is corrupted. Using default settings.")
        return default_config


def save_config(config_data):
    """保存配置到文件。"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)


def open_settings_window(parent):
    """打开设置窗口，包含语言和词云选项。"""
    settings_win = tk.Toplevel(parent)
    settings_win.title(_("settings_title"))
    settings_win.geometry("480x280")
    settings_win.resizable(False, False)
    settings_win.transient(parent)
    settings_win.grab_set()

    config = load_config()

    # --- NEW: 变量定义 ---
    tdl_path_var = tk.StringVar(value=config.get("tdl_path", "tdl"))
    proxy_var = tk.StringVar(value=config.get("proxy", ""))
    api_key_var = tk.StringVar(value=config.get("api", ""))
    lang_var = tk.StringVar(value=config.get("language", "zh"))
    wordcloud_var = tk.BooleanVar(value=config.get("generate_wordcloud", True))

    main_frame = ttk.Frame(settings_win, padding=15)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # --- UI 元素使用翻译函数 `_()` ---
    ttk.Label(main_frame, text=_("tdl_path")).grid(row=0, column=0, sticky=tk.W, pady=4)
    ttk.Entry(main_frame, textvariable=tdl_path_var, width=40).grid(row=0, column=1, sticky=tk.EW)

    ttk.Label(main_frame, text=_("proxy_address")).grid(row=1, column=0, sticky=tk.W, pady=4)
    ttk.Entry(main_frame, textvariable=proxy_var, width=40).grid(row=1, column=1, sticky=tk.EW)

    ttk.Label(main_frame, text=_("api_key")).grid(row=2, column=0, sticky=tk.W, pady=4)
    ttk.Entry(main_frame, textvariable=api_key_var, width=40, show="*").grid(row=2, column=1, sticky=tk.EW)

    ttk.Label(main_frame, text=_("language")).grid(row=3, column=0, sticky=tk.W, pady=4)
    lang_combo = ttk.Combobox(main_frame, textvariable=lang_var, values=["zh", "en"], state="readonly")
    lang_combo.grid(row=3, column=1, sticky=tk.EW)

    ttk.Checkbutton(main_frame, text=_("generate_wordcloud"), variable=wordcloud_var).grid(row=4, column=0,
                                                                                           columnspan=2, sticky=tk.W,
                                                                                           pady=8)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky=tk.E)

    def save_and_close():
        new_config = {
            "tdl_path": tdl_path_var.get(),
            "proxy": proxy_var.get(),
            "api": api_key_var.get(),
            "language": lang_var.get(),
            "generate_wordcloud": wordcloud_var.get()
        }
        save_config(new_config)
        messagebox.showinfo(_("success"), _("settings_saved"), parent=settings_win)
        settings_win.destroy()

    ttk.Button(button_frame, text=_("save"), command=save_and_close, style="Accent.TButton").pack(side=tk.RIGHT)
    ttk.Button(button_frame, text=_("cancel"), command=settings_win.destroy).pack(side=tk.RIGHT, padx=10)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        set_language(self.config.get("language", "zh"))

        self.title(_("window_title"))
        self.geometry("960x720")

        self.progress_queue = queue.Queue()

        self.build_ui()
        self.populate_tree_from_cache()
        self.process_queue()

    def process_queue(self):
        """处理来自工作线程的进度更新请求"""
        try:
            while True:
                status_key, value = self.progress_queue.get_nowait()
                self.status_label.config(text=_(status_key))
                if value >= 0:
                    self.progress_bar['value'] = value
                elif value == -1:  # 不确定进度
                    self.progress_bar.step(2)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

    def update_progress(self, status_key, value):
        """线程安全地更新进度条和状态"""
        self.progress_queue.put((status_key, value))

    def build_ui(self):
        # --- 主框架 ---
        left_frame = ttk.Frame(self, padding=10, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        left_frame.pack_propagate(False)

        right_frame = ttk.Frame(self, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- 左侧面板 ---
        load_button = ttk.Button(left_frame, text=_("load_chats"), command=self.start_load_chats_thread)
        load_button.pack(fill=tk.X, pady=5)

        export_frame = ttk.LabelFrame(left_frame, text=_("export_settings"), padding=10)
        export_frame.pack(fill=tk.X, pady=5)
        self.mode_var = tk.StringVar(value="msgs")
        self.number_var = tk.IntVar(value=100)
        ttk.Radiobutton(export_frame, text=_("recent_n_msgs"), variable=self.mode_var, value="msgs").pack(anchor=tk.W)
        ttk.Radiobutton(export_frame, text=_("recent_n_hours"), variable=self.mode_var, value="hours").pack(anchor=tk.W)
        input_frame = ttk.Frame(export_frame)
        input_frame.pack(fill=tk.X, pady=2, anchor=tk.W)
        ttk.Label(input_frame, text=_("n_equals")).pack(side=tk.LEFT)
        ttk.Entry(input_frame, textvariable=self.number_var, width=10).pack(side=tk.LEFT, padx=5)
        self.group_name_label = ttk.Label(export_frame, text=_("no_chat_selected"), foreground="blue")
        self.group_name_label.pack(fill=tk.X, pady=(5, 5))

        forward_frame = ttk.LabelFrame(left_frame, text=_("forward_settings"), padding=10)
        forward_frame.pack(fill=tk.X, pady=5)
        self.custom_target_var = tk.BooleanVar(value=False)
        self.chat_target_var = tk.StringVar()
        self.chat_target_entry = ttk.Entry(forward_frame, textvariable=self.chat_target_var, width=28, state="disabled")

        def on_custom_target_toggle():
            if self.custom_target_var.get():
                self.chat_target_entry.config(state="normal")
                if self.chat_target_entry.get() == _("forward_default"): self.chat_target_entry.delete(0, tk.END)
            else:
                self.chat_target_entry.delete(0, tk.END)
                self.chat_target_entry.insert(0, _("forward_default"))
                self.chat_target_entry.config(state="disabled")

        ttk.Checkbutton(forward_frame, text=_("forward_to_target"), variable=self.custom_target_var,
                        command=on_custom_target_toggle).pack(anchor=tk.W)
        self.chat_target_entry.pack(anchor=tk.W, pady=(5, 0))
        on_custom_target_toggle()

        summary_button = ttk.Button(left_frame, text=_("start_summary"), command=self.start_summary_thread,
                                    style="Accent.TButton")
        summary_button.pack(fill=tk.X, pady=20)
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Helvetica", 12, "bold"))

        # --- NEW: 进度条和状态标签 ---
        status_frame = ttk.Frame(left_frame, padding=(0, 10))
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        self.status_label = ttk.Label(status_frame, text=_("status_ready"))
        self.status_label.pack(fill=tk.X, anchor=tk.W)
        self.progress_bar = ttk.Progressbar(status_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(2, 0))

        settings_button = ttk.Button(left_frame, text=_("settings"), command=lambda: open_settings_window(self))
        settings_button.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # --- 右侧面板 ---
        tree_frame = ttk.LabelFrame(right_frame, text=_("chat_list"), padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        columns = ("ID", "Type", "VisibleName", "Username")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col); self.tree.column(col, width=150, anchor=tk.W)

        def on_chat_select(event):
            sel = self.tree.selection()
            if sel: self.group_name_label.config(text=_("current_chat").format(self.tree.item(sel[0])['values'][2]))

        self.tree.bind("<<TreeviewSelect>>", on_chat_select)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        results_frame = ttk.LabelFrame(right_frame, text=_("summary_results"), padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        results_frame.grid_rowconfigure(0, weight=1);
        results_frame.grid_columnconfigure(0, weight=3);
        results_frame.grid_columnconfigure(1, weight=2)
        self.summary_text_widget = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state="disabled",
                                                             font=("Helvetica", 10))
        self.summary_text_widget.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.wordcloud_frame = ttk.Frame(results_frame)
        self.wordcloud_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ttk.Label(self.wordcloud_frame, text=_("core_wordcloud"), font=("Helvetica", 11, "bold")).pack(pady=5)
        self.wordcloud_canvas = tk.Label(self.wordcloud_frame)
        self.wordcloud_canvas.pack(expand=True)

    def populate_tree(self, chats_data):
        """用从 tdl 获取的数据填充群聊列表树。"""
        # 清空旧数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 插入新数据
        for chat in chats_data:
            # --- 核心修正：使用小写开头的键名来匹配 tdl 的 JSON 输出 ---
            self.tree.insert("", tk.END, values=(
                chat.get('id'),
                chat.get('type'),
                chat.get('visible_name'),
                chat.get('username', '-')  # 如果没有 username，则显示 '-'
            ))
    def populate_tree_from_cache(self):
        """启动时从缓存文件加载群聊列表"""
        if CHATS_CACHE_FILE.exists():
            try:
                with open(CHATS_CACHE_FILE, 'r', encoding='utf-8') as f:
                    chats = json.load(f)
                self.populate_tree(chats)
                messagebox.showinfo(_("info"), _("load_chats_from_cache").format(len(chats)))
            except json.JSONDecodeError:
                pass  # 文件损坏，忽略

    def start_load_chats_thread(self):
        """在新线程中启动加载群聊任务"""
        thread = threading.Thread(target=self.load_chats_worker, daemon=True)
        thread.start()

    def load_chats_worker(self):
        """加载群聊列表的工作函数"""
        try:
            self.update_progress("status_loading_chats", 0)
            chats = chat_selector.list_chats(progress_callback=self.update_progress)

            with open(CHATS_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(chats, f, indent=2, ensure_ascii=False)

            self.populate_tree(chats)
            self.update_progress("status_done", 100)
            messagebox.showinfo(_("success"), _("load_chats_success").format(len(chats)))
        except Exception as e:
            self.update_progress("status_error", 100)
            messagebox.showerror(_("error"), _("load_chats_fail").format(e))

    def start_summary_thread(self):
        """在新线程中启动总结任务"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(_("warning"), _("invalid_selection"))
            return

        chat_id = self.tree.item(selected[0])['values'][0]
        thread = threading.Thread(target=self.summary_worker, args=(chat_id,), daemon=True)
        thread.start()

    def summary_worker(self, chat_id):
        """完整的总结工作流，在独立线程中运行"""
        try:
            # 1. 准备和验证
            self.update_progress("processing", 5)
            n = self.number_var.get()
            if n <= 0: raise ValueError(_("invalid_n"))

            self.summary_text_widget.config(state="normal");
            self.summary_text_widget.delete('1.0', tk.END);
            self.summary_text_widget.config(state="disabled")
            self.wordcloud_canvas.config(image=None);
            self.wordcloud_canvas.image = None
            self.update_idletasks()

            # 2. 导出
            if self.mode_var.get() == "msgs":
                exporter.export_chat(chat_id, last_n=n, progress_callback=self.update_progress)
            else:
                exporter.export_chat(chat_id, last_n_hours=n, progress_callback=self.update_progress)

            # 3. 过滤
            self.update_progress("status_filtering", 40)
            formatted_messages = filter_and_format_messages()
            if not formatted_messages: raise ValueError(_("no_valid_messages"))

            # 4. 总结
            self.update_progress("status_summarizing", 50)
            summary_text = summarizer.summarize_chat(formatted_messages)
            self.summary_text_widget.config(state="normal");
            self.summary_text_widget.insert('1.0', summary_text);
            self.summary_text_widget.config(state="disabled")

            # 5. 生成词云 (可选)
            if self.config.get("generate_wordcloud", True):
                self.update_progress("status_generating_wordcloud", 70)
                generate_wordcloud(summary_text, "../export/wordcloud.png")
                img = Image.open("../export/wordcloud.png");
                img_tk = ImageTk.PhotoImage(img)
                self.wordcloud_canvas.config(image=img_tk);
                self.wordcloud_canvas.image = img_tk

            # 6. 转发
            if self.custom_target_var.get():
                target_id = self.chat_target_var.get().strip()
                if not target_id: raise ValueError(_("forward_target_empty"))
            else:
                target_id = ""  # tdl 默认发到收藏夹

            forwarder.forward_summary(target_id, summary_text, progress_callback=self.update_progress)

            self.update_progress("status_done", 100)
            messagebox.showinfo(_("success"), _("summary_finished_and_forwarded"))

        except Exception as e:
            self.update_progress("status_error", 100)
            messagebox.showerror(_("error"), _("processing_failed").format(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()