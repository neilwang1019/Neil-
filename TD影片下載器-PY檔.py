import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread
import yt_dlp
import os

# 安裝所需的模組
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_modules = ['pillow', 'requests', 'yt-dlp', 'ffmpeg']

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        print(f"正在安裝 {module}...")
        install(module)
    else:
        print(f"{module} 已安裝。")

# 主類 VideoDownloaderApp，封裝所有邏輯
class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TD影片下載器")
        self.root.geometry("1024x768")
        self.root.configure(bg="#FFFFFF")

        self.folder_label_var = tk.StringVar()
        self.downloading = False
        self.agree_var = tk.BooleanVar()  # 新增接受條款的變數
        
        self.setup_ui()

    def setup_ui(self):
        # 標題
        header_label = ttk.Label(self.root, text="TD影片下載器", font=("Arial", 24, "bold"), anchor="center", background="white", foreground="#6A0DAD")
        header_label.grid(row=0, column=0, columnspan=2, pady=30, padx=10, sticky='ew')

        # 影片連結輸入
        self.setup_link_input()
        self.setup_video_options()
        self.setup_download_options()
        self.setup_progress_bar()
        self.setup_info_frame()

    def setup_link_input(self):
        link_frame = ttk.LabelFrame(self.root, text="影片連結", padding=(20, 10))
        link_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        
        self.link_entry = ttk.Entry(link_frame, font=("Arial", 16), width=80)
        self.link_entry.grid(row=0, column=0, pady=10, padx=10, sticky='ew')

        fetch_info_button = ttk.Button(link_frame, text="獲取影片品質", command=self.fetch_video_info)
        fetch_info_button.grid(row=0, column=1, padx=10, pady=10)
        
        download_button = ttk.Button(link_frame, text="開始下載", command=self.start_download_thread)
        download_button.grid(row=0, column=2, padx=10, pady=10)
        download_button['state'] = 'disabled'  # 初始設為無法點擊
        self.agree_var.trace("w", lambda *args: self.toggle_download_button(download_button))

    def toggle_download_button(self, download_button):
        if self.agree_var.get():
            download_button['state'] = 'normal'
        else:
            download_button['state'] = 'disabled'

    def setup_video_options(self):
        options_frame = ttk.LabelFrame(self.root, text="影片設定", padding=(20, 10))
        options_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='ew')

        # 影片品質選擇
        quality_label = ttk.Label(options_frame, text="影片品質", font=("Arial", 14), background="#FFFFFF", foreground="black")
        quality_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.quality_combobox = ttk.Combobox(options_frame, font=("Arial", 14), width=20)
        self.quality_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # 影片格式選擇
        format_label = ttk.Label(options_frame, text="影片格式", font=("Arial", 14), background="#FFFFFF", foreground="black")
        format_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.format_combobox = ttk.Combobox(options_frame, font=("Arial", 14), width=20, values=["完整版", "僅音檔", "僅畫面"])
        self.format_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.format_combobox.current(0)  # 預設選中「完整版」

    def setup_download_options(self):
        download_frame = ttk.LabelFrame(self.root, text="下載設定", padding=(20, 10))
        download_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky='ew')

        # 下載資料夾選擇
        folder_label = ttk.Label(download_frame, text="下載資料夾", font=("Arial", 14), background="#FFFFFF", foreground="black")
        folder_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        folder_button = ttk.Button(download_frame, text="選擇資料夾", command=self.select_folder)
        folder_button.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        folder_display = ttk.Label(download_frame, textvariable=self.folder_label_var, font=("Arial", 14), width=40, background="#FFFFFF", foreground="black", anchor="w")
        folder_display.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # 勾選接受條款的框
        agree_checkbox = ttk.Checkbutton(self.root, text="我已閱讀並接受使用條款及隱私政策", variable=self.agree_var)
        agree_checkbox.grid(row=4, column=0, columnspan=2, pady=10)

        # 隱私政策點擊提示
        privacy_label = ttk.Label(self.root, text="請點擊此處閱讀隱私政策", foreground="blue", cursor="hand2")
        privacy_label.grid(row=5, column=0, columnspan=2, pady=10)
        privacy_label.bind("<Button-1>", lambda e: self.show_privacy_policy())

    def setup_progress_bar(self):
        progress_frame = ttk.LabelFrame(self.root, text="下載進度", padding=(20, 10))
        progress_frame.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky='ew')

        self.progress_bar = ttk.Progressbar(progress_frame, length=800, mode='determinate')
        self.progress_bar.grid(row=0, column=0, pady=10, padx=10, sticky='ew')

    def setup_info_frame(self):
        info_frame = ttk.LabelFrame(self.root, text="支援平台及製作人", padding=(20, 10))
        info_frame.grid(row=7, column=0, columnspan=2, pady=20, padx=10, sticky='ew')

        platform_label = ttk.Label(info_frame, text="支持下載的平臺：\n- 任何公開影片連結", font=("Arial", 14))
        platform_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        creator_label = ttk.Label(info_frame, text="製作人: Neil道人\n感謝使用「影片下載器」！", font=("Arial", 14))
        creator_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    def start_download_thread(self):
        video_url = self.link_entry.get()
        download_folder = self.folder_label_var.get()
        
        if not video_url or not download_folder:
            messagebox.showwarning("錯誤", "請輸入影片連結並選擇下載路徑")
            return
        
        self.downloading = True
        download_thread = Thread(target=self.download_video, args=(video_url, download_folder))
        download_thread.start()

    def download_video(self, video_url, download_folder):
        selected_format = self.format_combobox.get()

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
        }

        if selected_format == "僅音檔":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',  # 使用 FFmpeg 來擷取音檔
                'preferredcodec': 'mp3',      # 優先選擇 MP3 格式
                'preferredquality': '192',     # 設定音質，根據需求調整
            }]
        elif selected_format == "僅畫面":
            ydl_opts['format'] = 'bestvideo'

        self.progress_bar['value'] = 0

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except yt_dlp.DownloadError as e:
            messagebox.showerror("錯誤", f"下載錯誤: {e}")
        except Exception as e:
            messagebox.showerror("錯誤", f"未知錯誤: {e}")
        finally:
            self.downloading = False

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                progress = d['downloaded_bytes'] / d['total_bytes'] * 100
                self.progress_bar['value'] = progress
                self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100
            messagebox.showinfo("完成", "下載完成！")

    def fetch_video_info(self):
        video_url = self.link_entry.get()
        
        if not video_url:
            messagebox.showwarning("錯誤", "請輸入影片連結")
            return

        try:
            with yt_dlp.YoutubeDL() as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                formats = info_dict.get('formats', [])
                quality_set = set()  # 使用集合來存儲質量，避免重複

                for f in formats:
                    if f['vcodec'] != 'none' and 'height' in f:
                        quality_set.add(f"{f['height']}p ({f['ext']})")

                if quality_set:
                    # 將集合轉換為列表並排序，以便展示
                    self.quality_combobox['values'] = sorted(list(quality_set))
                    self.quality_combobox.current(0)
                else:
                    self.quality_combobox['values'] = ["最佳"]
                    self.quality_combobox.current(0)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法獲取影片信息: {e}")

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        
        if folder_selected:
            self.folder_label_var.set(folder_selected)

    def show_privacy_policy(self):
        privacy_policy = """隱私政策

在使用本影片下載器（以下簡稱「本工具」）時，您的隱私對我們非常重要。此隱私政策將說明我們如何收集、使用和保護您的信息。

1. 信息收集
   - 我們不會主動收集您個人的識別信息，例如姓名、地址或聯絡電話。
   - 本工具在運行過程中不會收集或儲存您的下載記錄或影片連結。

2. 信息使用
   - 任何收集到的數據僅用於提供和改善本工具的服務。
   - 我們不會將您的信息與第三方分享。

3. 數據安全
   - 我們將採取合理的措施來保護您的信息不受到未經授權的訪問、泄露或損壞。

4. Cookies和追踪技術
   - 本工具不使用Cookies或類似的追踪技術來收集任何信息。

5. 條款更新
   - 我們可能會不定期更新本隱私政策，任何修改將在本工具內公告。建議您定期查看本政策以了解任何更改。

6. 創作人員
   - 感謝所有位本工具貢獻之人：
     - 主編寫:台灣小國一生 Neil道人
     - 優化協助: ChatGPT Gemini 等等AI

7. 聯絡握們
   - 歡迎聯絡我們，並告知可優化之地方：
     - 電子郵件：neilwang1019@gmail.com     

使用本工具即表示您了解並同意本隱私政策。如您不同意這些條款，請勿使用本工具。
"""
        messagebox.showinfo("隱私政策", privacy_policy)

# 主程式入口點
if __name__ == "__main__":
    root = tk.Tk()

    # 自訂樣式
    style = ttk.Style()
    
    # 設置自訂按鈕樣式
    style.configure("TButton",
                    font=("Arial", 16, "bold"),
                    padding=10,
                    background="#6A0DAD",
                    foreground="black",
                    relief="flat")

    style.map("TButton",
              background=[("active", "#5B009D"), ("disabled", "#cccccc")],
              foreground=[("active", "black"), ("disabled", "#666666")])

    # 設置自訂框架樣式
    style.configure("TLabelframe", background="#FFFFFF", foreground="black")
    style.configure("Horizontal.TProgressbar", troughcolor="#dddddd", background="#6A0DAD")

    app = VideoDownloaderApp(root)
    root.mainloop()
