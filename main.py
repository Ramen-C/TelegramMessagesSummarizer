import tkinter as tk
from tkinter import ttk, messagebox
import chat_selector, exporter, summarizer, forwarder
import json
import subprocess


def main():
    root = tk.Tk()
    root.title("Telegram 群聊助手")
    root.geometry("800x600")

    # 左侧：载入群聊、导出设置、开始总结按钮
    left_frame = ttk.Frame(root, padding=10)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)


    # 载入群聊按钮事件
    def load_chats():
        try:
            chats = chat_selector.list_chats()
            # 清空表格
            for item in tree.get_children():
                tree.delete(item)
            # 插入群聊列表
            for chat in chats:
                tree.insert("", tk.END, values=(
                    chat['id'],  # 群聊ID
                    chat['type'],  # 群聊类型
                    chat['visible_name'],  # 显示名称
                    chat.get('username', '-'),  # 用户名（可能不存在）
                ))
        except Exception as e:
            messagebox.showinfo("成功", f"已载入 {len(chats)} 个群聊")

    load_button = ttk.Button(left_frame, text="载入群聊", command=load_chats)
    load_button.pack(fill=tk.X, pady=5)

    # 导出设置：单选按钮和数字输入框
    export_frame = ttk.LabelFrame(left_frame, text="导出设置", padding=10)
    export_frame.pack(fill=tk.X, pady=5)
    mode_var = tk.StringVar()
    rb_msgs = ttk.Radiobutton(export_frame, text="最近 N 条", variable=mode_var, value="msgs")
    rb_hours = ttk.Radiobutton(export_frame, text="最近 N 小时", variable=mode_var, value="hours")
    rb_msgs.pack(anchor=tk.W)
    rb_hours.pack(anchor=tk.W)
    input_frame = ttk.Frame(export_frame)
    input_frame.pack(fill=tk.X, pady=2)
    ttk.Label(input_frame, text="N = ").pack(side=tk.LEFT)
    number_var = tk.IntVar()
    entry = ttk.Entry(input_frame, textvariable=number_var, state="disabled", width=10)
    entry.pack(side=tk.LEFT, padx=5)
    def on_mode_change():
        entry.config(state="normal")
    rb_msgs.config(command=on_mode_change)
    rb_hours.config(command=on_mode_change)

    # 收藏夹设置，待补充
    to_fav_var = tk.BooleanVar()
    to_fav_check = ttk.Checkbutton(export_frame, text="导出到收藏夹", variable=to_fav_var)
    to_fav_check.pack(anchor=tk.W)

    ttk.Label(export_frame, text="导出目标 CHAT:").pack(anchor=tk.W, pady=(10, 0))
    chat_target_var = tk.StringVar()
    chat_target_entry = ttk.Entry(export_frame, textvariable=chat_target_var, width=30)
    chat_target_entry.pack(anchor=tk.W)


    # 开始总结按钮事件
    def start_summary():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("未选择群聊", "请先选择一个群聊")
            return
        if mode_var.get() == "":
            messagebox.showwarning("未选择导出方式", "请选择导出方式")
            return
        chat_id = tree.item(selected[0])['values'][0]
        try:
            n = number_var.get()
            if n <= 0:
                raise ValueError("N 必须为正整数")
            if mode_var.get() == "msgs":
                exporter.export_chat(chat_id, last_n=n)
            else:
                exporter.export_chat(chat_id, last_n_hours=n)
            summary_text = summarizer.summarize_chat()
            forwarder.forward_summary(chat_target_var.get().strip(), summary_text)
            messagebox.showinfo("成功", "摘要已发送到群聊")
        except Exception as e:
            messagebox.showerror("错误", f"总结失败: {e}")

    summary_button = ttk.Button(left_frame, text="开始总结", command=start_summary)
    summary_button.pack(fill=tk.X, pady=5)

    # 右侧：群聊列表表格和选中群聊信息
    right_frame = ttk.Frame(root, padding=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    columns = ("ID", "Type", "VisibleName", "Username")
    tree = ttk.Treeview(right_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.W)
    # 绑定选中事件
    def on_chat_select(event):
        sel = tree.selection()
        if sel:
            item = tree.item(sel[0])
            vals = item['values']
            cid, cname = vals[0], vals[2]
            selected_label.config(text=f"选中群聊: ID={cid}, 名称={cname}")
    tree.bind("<<TreeviewSelect>>", on_chat_select)
    scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    selected_label = ttk.Label(right_frame, text="未选择群聊")
    selected_label.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    root.mainloop()

if __name__ == "__main__":
    main()