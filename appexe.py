from flask import Flask, render_template, request, flash, redirect, url_for, session
from smb.SMBConnection import SMBConnection
import subprocess
import socket
import string
import ctypes
import sys
import os
import webview  # 引入桌面視窗套件

# 判斷是否被 PyInstaller 打包成單一執行檔
if getattr(sys, 'frozen', False):
    # 如果是打包狀態，取得解壓縮後的暫存目錄
    base_dir = sys._MEIPASS
else:
    # 如果是開發環境，就用目前的目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))

# 指定 templates 資料夾的絕對路徑
template_dir = os.path.join(base_dir, 'templates')

# 初始化 Flask 時，明確告訴它 templates 的位置
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'super_secret_key_for_flash_messages'

# 設定 Windows 隱藏背景執行視窗的參數
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

def get_available_drives():
    available_drives = []
    try:
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for i, letter in enumerate(string.ascii_uppercase):
            if not (bitmask & (1 << i)):
                if letter not in ['A', 'B', 'C']:
                    available_drives.append(f"{letter}:")
    except Exception:
        available_drives = [f"{chr(i)}:" for i in range(68, 91)]
    return available_drives

def get_mounted_shares_dict(target_ip):
    mounted_folders = {}
    mpr = ctypes.windll.mpr
    
    for letter in string.ascii_uppercase:
        drive = f"{letter}:"
        local_name = ctypes.create_unicode_buffer(drive)
        remote_name = ctypes.create_unicode_buffer(1024)
        length = ctypes.c_ulong(1024)
        
        result = mpr.WNetGetConnectionW(local_name, remote_name, ctypes.byref(length))
        
        if result == 0:
            network_path = remote_name.value
            if target_ip.lower() in network_path.lower():
                folder_name = network_path.rstrip('\\').split('\\')[-1]
                mounted_folders[folder_name] = drive
                
    return mounted_folders

def get_nas_shares(ip, username, password):
    try:
        conn = SMBConnection(username, password, socket.gethostname(), "SynologyNAS", use_ntlm_v2=True)
        assert conn.connect(ip, 139)
        
        shares = conn.listShares()
        folder_names = []
        for share in shares:
            if not share.isSpecial and share.name not in ['IPC$', 'print$']:
                folder_names.append(share.name)
        
        conn.close()
        return folder_names, None
    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ip = request.form.get('nas_ip')
        username = request.form.get('username')
        password = request.form.get('password')

        folders, error = get_nas_shares(ip, username, password)
        
        if folders is not None:
            session['credentials'] = {'ip': ip, 'username': username, 'password': password}
            session['folders'] = folders
            flash("✅ 成功獲取資料夾清單", "success")
        else:
            flash(f"❌ 無法連線或獲取資料夾: {error}", "danger")
            session.pop('folders', None) 

    credentials = session.get('credentials', {})
    folders = session.get('folders', [])
    
    mounted_folders = {}
    if credentials.get('ip') and folders:
        mounted_folders = get_mounted_shares_dict(credentials['ip'])

    drive_letters = get_available_drives()

    return render_template('index.html', 
                           folders=folders, 
                           credentials=credentials, 
                           drive_letters=drive_letters,
                           mounted_folders=mounted_folders)

@app.route('/mount', methods=['POST'])
def mount():
    credentials = session.get('credentials')
    if not credentials:
        return redirect(url_for('index'))

    ip = credentials.get('ip')
    username = credentials.get('username')
    password = credentials.get('password')
    folder = request.form.get('folder')
    drive_letter = request.form.get('drive_letter')

    network_path = rf"\\{ip}\{folder}"
    command = ['net', 'use', drive_letter, network_path, f'/user:{username}', password]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True, creationflags=CREATE_NO_WINDOW)
        flash(f"✅ 成功將 {network_path} 掛載至 {drive_letter}", "success")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else e.stdout.strip()
        flash(f"❌ 掛載失敗: {error_msg}", "danger")

    return redirect(url_for('index'))

@app.route('/unmount', methods=['POST'])
def unmount():
    drive_letter = request.form.get('drive_letter')
    command = ['net', 'use', drive_letter, '/delete', '/y']
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True, creationflags=CREATE_NO_WINDOW)
        flash(f"✅ 成功卸載磁碟機 {drive_letter}", "success")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else e.stdout.strip()
        flash(f"❌ 卸載失敗: {error_msg}", "danger")
        
    return redirect(url_for('index'))

@app.route('/unmount_all', methods=['POST'])
def unmount_all():
    credentials = session.get('credentials')
    if not credentials:
        return redirect(url_for('index'))

    target_ip = credentials.get('ip')
    mounted_folders = get_mounted_shares_dict(target_ip)

    if not mounted_folders:
        flash(f"⚠️ 目前沒有偵測到任何與 {target_ip} 連線的磁碟機。", "info")
        return redirect(url_for('index'))

    success_list = []
    error_list = []

    for folder, drive in mounted_folders.items():
        command = ['net', 'use', drive, '/delete', '/y']
        try:
            subprocess.run(command, capture_output=True, text=True, check=True, creationflags=CREATE_NO_WINDOW)
            success_list.append(drive)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else e.stdout.strip()
            error_list.append(f"{drive} ({error_msg})")

    if not error_list:
        flash(f"✅ 成功卸載所有磁碟機: {', '.join(success_list)}", "success")
    else:
        flash(f"⚠️ 部分卸載完成。成功: {', '.join(success_list)} | 失敗: {', '.join(error_list)}", "warning")

    return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("✅ 已清除連線狀態", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 建立桌面應用程式視窗，設定寬度 800、高度 600，並且禁止縮放視窗 (resizable=False)
    window = webview.create_window(
        'NAS 網路硬碟掛載 Pro', 
        app, 
        width=800, 
        height=600, 
        resizable=False
    )
    webview.start()
