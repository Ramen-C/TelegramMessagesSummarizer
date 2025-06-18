import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, scrolledtext
from translations import _

from core.loadhelper import load_config, save_config


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

    # Define a bold font based on the default font
    default_font = tkfont.nametofont("TkDefaultFont")
    bold_font = default_font.copy()
    bold_font.configure(weight="bold")

    # Create a new style using that font
    style = ttk.Style()
    style.configure("Bold.TButton", font=bold_font)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky=tk.E)

    save_button = ttk.Button(button_frame, text=_("save"), command=save_and_close, style="Bold.TButton")
    cancel_button = ttk.Button(button_frame, text=_("cancel"), command=settings_win.destroy)

    save_button.grid(row=0, column=1, padx=(20, 0), sticky=tk.EW)
    cancel_button.grid(row=0, column=0, padx=(0, 20), sticky=tk.EW)

    # Make both columns expand equally
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

