# login.py
import subprocess

def login_tdl():
    """
    使用 tdl 登录 Telegram Desktop 客户端。如果出现“登出现有会话”的提示，自动回复 no。
    """
    # 启动 tdl 登录命令
    proc = subprocess.Popen(['tdl', 'login'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # 向 stdin 发送 'no\n' 以跳过退出现有会话提示
    stdout, stderr = proc.communicate(input='no\n')
    if proc.returncode != 0:
        raise RuntimeError(f"TDL 登录失败，错误信息：{stderr}")
    print("TDL 登录成功。")