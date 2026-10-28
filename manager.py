import os
import sys
import shutil
import re
import json
import base64
import urllib.request
import urllib.error
import webbrowser
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(SCRIPT_DIR, "index.html")
ZIP_FILE = os.path.join(SCRIPT_DIR, "flexeditor-website.zip")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "github_settings.cfg")

class WebsiteManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FLEXEditor Website Manager - Screenshots & GitHub Cloudflare Sync")
        self.geometry("680x740")
        self.minsize(580, 650)
        self.configure(bg="#0c101d")

        # Visual Theme
        self.col_bg = "#0c101d"
        self.col_card = "#141b2d"
        self.col_border = "#263554"
        self.col_accent = "#2f79fd"
        self.col_text = "#f1f5f9"
        self.col_muted = "#94a3b8"

        self.gh_repo = "iamemby-websites/FLEXEditor.download"
        self.gh_branch = "main"
        self.gh_token = ""
        self.gh_autosync = True
        self.load_github_config()

        self.setup_ui()

    def load_github_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("Repo="):
                            self.gh_repo = line.split("=", 1)[1].strip()
                        elif line.startswith("Branch="):
                            self.gh_branch = line.split("=", 1)[1].strip()
                        elif line.startswith("Token="):
                            self.gh_token = line.split("=", 1)[1].strip()
                        elif line.startswith("AutoSync="):
                            self.gh_autosync = line.split("=", 1)[1].strip().lower() == "true"
            except Exception:
                pass

    def setup_ui(self):
        # Header Frame
        hdr_frame = tk.Frame(self, bg=self.col_bg, pady=14)
        hdr_frame.pack(fill="x", padx=20)

        title_lbl = tk.Label(hdr_frame, text="FLEXEditor Website Manager", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg=self.col_bg)
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(hdr_frame, text="Manage screenshots, update index.html, and sync directly with GitHub & Cloudflare Pages.", font=("Segoe UI", 9), fg=self.col_muted, bg=self.col_bg)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # GitHub Status Bar
        gh_status_frame = tk.Frame(self, bg="#10172a", bd=1, relief="solid", highlightbackground=self.col_border, highlightthickness=1, padx=12, pady=6)
        gh_status_frame.pack(fill="x", padx=20, pady=(0, 10))

        gh_info = f"GitHub: {self.gh_repo} ({self.gh_branch}) • Auto-Sync: {'ON' if self.gh_autosync else 'OFF'}"
        self.gh_lbl = tk.Label(gh_status_frame, text=gh_info, font=("Segoe UI", 9, "bold"), fg="#60a5fa", bg="#10172a")
        self.gh_lbl.pack(side="left")

        # Container for screenshot cards
        cards_container = tk.Frame(self, bg=self.col_bg)
        cards_container.pack(fill="both", expand=True, padx=20, pady=0)

        # Slot 1
        self.card_slot1 = self.create_slot_card(
            cards_container, slot_id=1,
            title="Screenshot 1: Main Workstation Interface",
            default_caption="FLEXEditor - Main Workstation Interface",
            target_filename="screenshot1.png"
        )
        self.card_slot1.pack(fill="x", pady=5)

        # Slot 2
        self.card_slot2 = self.create_slot_card(
            cards_container, slot_id=2,
            title="Screenshot 2: Layer Timeline & Editing",
            default_caption="Layer Timeline & Precision Editing",
            target_filename="screenshot2.png"
        )
        self.card_slot2.pack(fill="x", pady=5)

        # Slot 3
        self.card_slot3 = self.create_slot_card(
            cards_container, slot_id=3,
            title="Screenshot 3: Color Grading & Inspector",
            default_caption="3-Way Color Wheels & Inspector",
            target_filename="screenshot3.png"
        )
        self.card_slot3.pack(fill="x", pady=5)

        # Action Buttons Bar
        actions_frame = tk.Frame(self, bg=self.col_bg, pady=12)
        actions_frame.pack(fill="x", padx=20)

        btn_preview = tk.Button(
            actions_frame, text="🌐 Preview Website", font=("Segoe UI", 10, "bold"),
            bg="#1d4ed8", fg="#ffffff", activebackground="#2563eb", activeforeground="#ffffff",
            bd=0, padx=12, pady=7, cursor="hand2", command=self.preview_website
        )
        btn_preview.pack(side="left", padx=(0, 8))

        btn_push = tk.Button(
            actions_frame, text="🚀 Push All to GitHub", font=("Segoe UI", 10, "bold"),
            bg="#059669", fg="#ffffff", activebackground="#10b981", activeforeground="#ffffff",
            bd=0, padx=12, pady=7, cursor="hand2", command=self.push_all_to_github
        )
        btn_push.pack(side="left", padx=(0, 8))

        btn_zip = tk.Button(
            actions_frame, text="📦 Cloudflare ZIP", font=("Segoe UI", 10, "bold"),
            bg="#263554", fg="#ffffff", activebackground="#334770", activeforeground="#ffffff",
            bd=0, padx=12, pady=7, cursor="hand2", command=self.generate_zip
        )
        btn_zip.pack(side="left")

        # Bottom status label
        self.status_lbl = tk.Label(self, text="Ready. Select any screenshot to upload.", font=("Segoe UI", 8), fg=self.col_muted, bg=self.col_bg, pady=6)
        self.status_lbl.pack(side="bottom", fill="x")

    def create_slot_card(self, parent, slot_id, title, default_caption, target_filename):
        card = tk.Frame(parent, bg=self.col_card, bd=1, relief="solid", highlightbackground=self.col_border, highlightthickness=1, padx=12, pady=8)

        top_row = tk.Frame(card, bg=self.col_card)
        top_row.pack(fill="x", pady=(0, 4))

        t_lbl = tk.Label(top_row, text=title, font=("Segoe UI", 10, "bold"), fg=self.col_accent, bg=self.col_card)
        t_lbl.pack(side="left")

        target_path = os.path.join(SCRIPT_DIR, target_filename)
        status_text = "✓ Present" if os.path.exists(target_path) else "○ Empty"
        status_color = "#34d399" if os.path.exists(target_path) else self.col_muted

        s_lbl = tk.Label(top_row, text=status_text, font=("Segoe UI", 8, "bold"), fg=status_color, bg=self.col_card)
        s_lbl.pack(side="right")

        mid_row = tk.Frame(card, bg=self.col_card)
        mid_row.pack(fill="x", pady=(0, 6))

        c_lbl = tk.Label(mid_row, text="Caption:", font=("Segoe UI", 8), fg=self.col_muted, bg=self.col_card)
        c_lbl.pack(side="left", padx=(0, 6))

        caption_var = tk.StringVar(value=default_caption)
        c_entry = tk.Entry(mid_row, textvariable=caption_var, font=("Segoe UI", 8), bg="#0c101d", fg="#ffffff", insertbackground="#ffffff", bd=1, relief="solid")
        c_entry.pack(side="left", fill="x", expand=True)

        btn_upload = tk.Button(
            card, text=f"📁 Upload Image for Slot {slot_id}", font=("Segoe UI", 8, "bold"),
            bg="#2563eb", fg="#ffffff", activebackground="#2f79fd", activeforeground="#ffffff",
            bd=0, padx=10, pady=5, cursor="hand2",
            command=lambda: self.upload_screenshot(slot_id, target_filename, caption_var.get(), s_lbl)
        )
        btn_upload.pack(anchor="e")

        return card

    def upload_screenshot(self, slot_id, target_filename, caption, status_label):
        file_path = filedialog.askopenfilename(
            title=f"Select Screenshot for Slot {slot_id}",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            target_path = os.path.join(SCRIPT_DIR, target_filename)
            shutil.copy2(file_path, target_path)

            self.update_html_slot(slot_id, target_filename, caption)
            status_label.config(text="✓ Updated", fg="#34d399")
            self.generate_zip(silent=True)

            # Auto-sync to GitHub if configured
            gh_synced = False
            if self.gh_autosync and self.gh_token:
                self.status_lbl.config(text="Pushing to GitHub...", fg="#60a5fa")
                self.update_idletasks()
                ok1, _ = self.push_file_to_github(target_filename)
                ok2, _ = self.push_file_to_github("index.html")
                gh_synced = ok1 and ok2

            msg = f"Screenshot {slot_id} saved as '{target_filename}' and index.html updated!"
            if gh_synced:
                msg += "\n\n✓ Changes automatically pushed to GitHub! Cloudflare will deploy in a few seconds."
            self.status_lbl.config(text="Done!", fg="#34d399")
            messagebox.showinfo("Success", msg)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload screenshot:\n{e}")

    def update_html_slot(self, slot_id, filename, caption):
        if not os.path.exists(HTML_FILE):
            raise FileNotFoundError("index.html not found.")

        with open(HTML_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        img_pattern = rf'(<img\s+id=["\']img-slot-{slot_id}["\'][^>]*src=["\'])[^"\']*(["\'])'
        if re.search(img_pattern, content):
            content = re.sub(img_pattern, rf'\g<1>{filename}\g<2>', content)

        if caption:
            caption_pattern = rf'(<span\s+id=["\']caption-slot-{slot_id}["\'][^>]*>)[^<]*(</span>)'
            if re.search(caption_pattern, content):
                content = re.sub(caption_pattern, rf'\g<1>{caption}\g<2>', content)

        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(content)

    def push_file_to_github(self, filename):
        file_path = os.path.join(SCRIPT_DIR, filename)
        if not os.path.exists(file_path) or not self.gh_token:
            return False, "File missing or Token not configured"

        try:
            with open(file_path, "rb") as f:
                b64_content = base64.b64encode(f.read()).decode("utf-8")

            get_url = f"https://api.github.com/repos/{self.gh_repo}/contents/{filename}?ref={self.gh_branch}"
            req = urllib.request.Request(get_url, headers={
                "Authorization": f"token {self.gh_token}",
                "User-Agent": "FLEXEditor-Manager",
                "Accept": "application/vnd.github.v3+json"
            })

            sha = None
            try:
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    sha = data.get("sha")
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    pass

            put_url = f"https://api.github.com/repos/{self.gh_repo}/contents/{filename}"
            payload = {
                "message": f"Update {filename} via Website Manager",
                "content": b64_content,
                "branch": self.gh_branch
            }
            if sha:
                payload["sha"] = sha

            put_req = urllib.request.Request(put_url, data=json.dumps(payload).encode("utf-8"), headers={
                "Authorization": f"token {self.gh_token}",
                "User-Agent": "FLEXEditor-Manager",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }, method="PUT")

            with urllib.request.urlopen(put_req) as resp:
                return True, "Uploaded"

        except Exception as e:
            return False, str(e)

    def push_all_to_github(self):
        if not self.gh_token:
            messagebox.showerror("GitHub Error", "GitHub token is missing in github_settings.cfg")
            return

        files = ["index.html", "flexeditoricon.png", "flexeditor.svg", "motion-preset-thumbnail.jpg"]
        for f in ["screenshot.png", "screenshot1.png", "screenshot2.png", "screenshot3.png"]:
            if os.path.exists(os.path.join(SCRIPT_DIR, f)):
                files.append(f)

        self.status_lbl.config(text="Pushing files to GitHub...", fg="#60a5fa")
        self.update_idletasks()

        success_count = 0
        for f in files:
            ok, _ = self.push_file_to_github(f)
            if ok:
                success_count += 1

        self.status_lbl.config(text=f"Pushed {success_count}/{len(files)} files to GitHub.", fg="#34d399")
        messagebox.showinfo("GitHub Sync Complete", f"Successfully pushed {success_count} files to:\nhttps://github.com/{self.gh_repo}\n\nCloudflare Pages will build the latest changes!")

    def preview_website(self):
        if os.path.exists(HTML_FILE):
            webbrowser.open(f"file://{os.path.abspath(HTML_FILE)}")
        else:
            messagebox.showerror("Error", "index.html not found!")

    def generate_zip(self, silent=False):
        try:
            files_to_zip = []
            for root, dirs, files in os.walk(SCRIPT_DIR):
                for f in files:
                    if f.endswith((".html", ".png", ".jpg", ".jpeg", ".webp", ".svg")):
                        files_to_zip.append(os.path.join(root, f))

            with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in files_to_zip:
                    arcname = os.path.relpath(file, SCRIPT_DIR)
                    zipf.write(file, arcname)

            if not silent:
                messagebox.showinfo("ZIP Created", f"Successfully generated:\n{os.path.basename(ZIP_FILE)}")
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"Failed to create ZIP archive:\n{e}")

if __name__ == "__main__":
    app = WebsiteManagerApp()
    app.mainloop()
