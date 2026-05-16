# NasMounter
```markdown
# 🚀 NAS Mounter Pro (NAS 網路硬碟掛載工具)

👉 **[點此下載最新版 EXE 執行檔](https://github.com/00086/NasMounter/releases/download/%23NasMounter/appexe.exe)**

![Windows](https://img.shields.io/badge/OS-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

**NAS Mounter Pro** 是一個現代化、具備圖形介面 (GUI) 的 Windows 網路硬碟掛載工具。
告別繁瑣的指令碼與 Windows 內建的網路磁碟機設定，本工具提供直覺、美觀的介面，讓使用者能輕鬆地連線至 NAS、列出共用資料夾，並一鍵掛載或卸載本機磁碟機。

## ✨ 核心特色功能

* 🖥️ **現代化圖形介面**：使用 Bootstrap 5 打造，支援流暢的桌面應用程式體驗。
* 🔌 **精準的底層連線**：基於 SMB 協定 (支援 NTLMv2)，能穩定獲取 Synology 等各大廠牌 NAS 的共用資料夾。
* 🖲️ **智慧磁碟機代號**：自動偵測本機已占用與可用的磁碟機代號（排除 A, B, C 等系統保留槽）。
* 🧹 **一鍵管理**：支援單一資料夾掛載/卸載，以及「一鍵強制卸載」所有已連線的網路磁碟機。
* 📦 **單一執行檔**：可完美打包為免安裝的單一 `.exe` 執行檔，不帶任何拖油瓶，方便隨身攜帶與部署。

---

## 🛠️ 開發語言與技術棧

* **後端邏輯**：Python 3
* **前端介面**：HTML5, CSS3 (Bootstrap 5)
* **桌面視窗容器**：PyWebView (結合 Flask)
* **系統調用**：Windows API (`ctypes`), `subprocess`

---

## 📦 安裝與執行 (開發環境)

若你要直接透過 Python 原始碼執行本程式，請先確保你的電腦已安裝 **Python 3.8 或以上版本**，並位於 Windows 作業系統下。

### 1. 複製專案
```bash
git clone [https://github.com/00086/NAS-Mounter-Pro.git](https://github.com/00086/NAS-Mounter-Pro.git)
cd NAS-Mounter-Pro

```

### 2. 安裝必要的 Python 模組

本程式依賴以下第三方套件，請透過 `pip` 進行安裝：

```bash
pip install Flask pysmb pywebview

```

*(註：其餘如 `subprocess`, `socket`, `ctypes` 皆為 Python 內建標準函式庫，無需額外安裝)*

### 3. 執行程式

請確保 `appexe.py` 與 `templates/index.html` 處於正確的目錄結構下，然後執行：

```bash
python appexe.py

```

---

## 📖 使用簡易說明

1. **連線至 NAS**：
* 在左側欄位輸入 NAS 的 **IP 位址**（例如：`192.168.1.100`）。
* 輸入具備存取權限的 **帳號** 與 **密碼**。
* 點擊「**列出資料夾**」。


2. **掛載資料夾**：
* 連線成功後，右側表格會列出該 NAS 上所有可用的共用資料夾。
* 在欲掛載的資料夾旁，透過下拉選單選擇一個**未使用的磁碟機代號**（如 `Z:`）。
* 點擊「**掛載**」，成功後狀態會變更為「已掛載」。


3. **卸載資料夾**：
* 針對已掛載的項目，點擊右側的「**卸載**」按鈕即可斷開連線。
* 若需一次清除所有連線，可點擊左下方的「**一鍵卸載全部**」。



---

## 🏗️ 如何打包為單一 EXE 執行檔

如果你想將此程式發布給沒有安裝 Python 環境的使用者，可以使用 `PyInstaller` 進行打包：

1. 安裝 PyInstaller：
```bash
pip install pyinstaller

```


2. 執行以下打包指令（請於專案根目錄執行）：
```bash
pyinstaller --noconsole --onefile --add-data "templates;templates" appexe.py

```


3. 打包完成後，可以在 `dist` 資料夾中找到 `app.exe`。這是一個完全獨立的執行檔，可直接在 Windows 10/11 上雙擊運行。

---

## ⚠️ 注意事項

* 本程式專為 **Windows 作業系統** 設計（底層依賴 `net use` 與 `mpr.dll` 等 Windows API），不適用於 macOS 或 Linux。
* 在某些特殊 Windows 版本（如教育版）下，若畫面出現比例裁切問題，程式內部已透過響應式斷點與版面鎖定（Fixed Layout）機制處理完畢，請安心使用。

## 📜 授權條款

本專案採用 [MIT License](LICENSE) 授權。歡迎自由修改與散布！

