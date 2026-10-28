import os
import sys
import shutil
import re
import webbrowser
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

# Base folder is the folder where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(SCRIPT_DIR, "index.html")
ZIP_FILE = os.path.join(SCRIPT_DIR, "flexeditor-website.zip")

class WebsiteManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FLEXEditor Website Manager - Screenshots & Content")
        self.geometry("640x680")
        self.minsize(560, 600)
        self.configure(bg="#0c101d")

        # Fonts & Colors
        self.col_bg = "#0c101d"
        self.col_card = "#141b2d"
        self.col_border = "#263554"
        self.col_accent = "#2f79fd"
        self.col_text = "#f1f5f9"
        self.col_muted = "#94a3b8"

        self.setup_ui()

    def setup_ui(self):
        # Header
        hdr_frame = tk.Frame(self, bg=self.col_bg, pady=16)
        hdr_frame.pack(fill="x", padx=20)

        title_lbl = tk.Label(hdr_frame, text="FLEXEditor Website Manager", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg=self.col_bg)
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(hdr_frame, text="Upload your application screenshots and update index.html instantly.", font=("Segoe UI", 9), fg=self.col_muted, bg=self.col_bg)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Container for screenshot cards
        cards_container = tk.Frame(self, bg=self.col_bg)
        cards_container.pack(fill="both", expand=True, padx=20, pady=5)

        # Slot 1: Main Workstation Interface
        self.card_slot1 = self.create_slot_card(
            cards_container,
            slot_id=1,
            title="Screenshot 1: Main Workstation Interface",
            default_caption="FLEXEditor - Main Workstation Interface",
            target_filename="screenshot1.png"
        )
        self.card_slot1.pack(fill="x", pady=6)

        # Slot 2: Timeline & Layers
        self.card_slot2 = self.create_slot_card(
            cards_container,
            slot_id=2,
            title="Screenshot 2: Layer Timeline & Editing",
            default_caption="Layer Timeline & Precision Editing",
            target_filename="screenshot2.png"
        )
        self.card_slot2.pack(fill="x", pady=6)

        # Slot 3: Color Grading & Inspector
        self.card_slot3 = self.create_slot_card(
            cards_container,
            slot_id=3,
            title="Screenshot 3: Color Grading & Inspector",
            default_caption="3-Way Color Wheels & Inspector",
            target_filename="screenshot3.png"
        )
        self.card_slot3.pack(fill="x", pady=6)

        # Bottom Actions Bar
        actions_frame = tk.Frame(self, bg=self.col_bg, pady=16)
        actions_frame.pack(fill="x", padx=20)

        btn_preview = tk.Button(
            actions_frame, text="🌐 Preview Website in Browser", font=("Segoe UI", 10, "bold"),
            bg="#1d4ed8", fg="#ffffff", activebackground="#2563eb", activeforeground="#ffffff",
            bd=0, padx=14, pady=8, cursor="hand2", command=self.preview_website
        )
        btn_preview.pack(side="left", padx=(0, 10))

        btn_zip = tk.Button(
            actions_frame, text="📦 Re-Generate Cloudflare ZIP", font=("Segoe UI", 10, "bold"),
            bg="#263554", fg="#ffffff", activebackground="#334770", activeforeground="#ffffff",
            bd=0, padx=14, pady=8, cursor="hand2", command=self.generate_zip
        )
        btn_zip.pack(side="left")

        # Status text
        self.status_lbl = tk.Label(self, text="Ready. Choose a screenshot to upload.", font=("Segoe UI", 8), fg=self.col_muted, bg=self.col_bg, pady=8)
        self.status_lbl.pack(side="bottom", fill="x")

    def create_slot_card(self, parent, slot_id, title, default_caption, target_filename):
        card = tk.Frame(parent, bg=self.col_card, bd=1, relief="solid", highlightbackground=self.col_border, highlightthickness=1, padx=14, pady=10)

        # Top row: Title and Status
        top_row = tk.Frame(card, bg=self.col_card)
        top_row.pack(fill="x", pady=(0, 6))

        t_lbl = tk.Label(top_row, text=title, font=("Segoe UI", 11, "bold"), fg=self.col_accent, bg=self.col_card)
        t_lbl.pack(side="left")

        target_path = os.path.join(SCRIPT_DIR, target_filename)
        status_text = "✓ Present" if os.path.exists(target_path) else "○ Empty"
        status_color = "#34d399" if os.path.exists(target_path) else self.col_muted

        s_lbl = tk.Label(top_row, text=status_text, font=("Segoe UI", 9, "bold"), fg=status_color, bg=self.col_card)
        s_lbl.pack(side="right")

        # Caption Entry
        mid_row = tk.Frame(card, bg=self.col_card)
        mid_row.pack(fill="x", pady=(0, 8))

        c_lbl = tk.Label(mid_row, text="Caption:", font=("Segoe UI", 9), fg=self.col_muted, bg=self.col_card)
        c_lbl.pack(side="left", padx=(0, 8))

        caption_var = tk.StringVar(value=default_caption)
        c_entry = tk.Entry(mid_row, textvariable=caption_var, font=("Segoe UI", 9), bg="#0c101d", fg="#ffffff", insertbackground="#ffffff", bd=1, relief="solid")
        c_entry.pack(side="left", fill="x", expand=True)

        # Upload Button
        btn_upload = tk.Button(
            card, text=f"📁 Select & Upload Image for Slot {slot_id}", font=("Segoe UI", 9, "bold"),
            bg="#2563eb", fg="#ffffff", activebackground="#2f79fd", activeforeground="#ffffff",
            bd=0, padx=10, pady=6, cursor="hand2",
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
            # Copy to website directory
            target_path = os.path.join(SCRIPT_DIR, target_filename)
            shutil.copy2(file_path, target_path)

            # Update index.html
            self.update_html_slot(slot_id, target_filename, caption)

            # Update status label
            status_label.config(text="✓ Updated", fg="#34d399")
            self.status_lbl.config(text=f"Slot {slot_id} updated with {os.path.basename(file_path)}!", fg="#34d399")

            # Also update zip
            self.generate_zip(silent=True)

            messagebox.showinfo(
                "Screenshot Uploaded",
                f"Screenshot {slot_id} has been saved as '{target_filename}' and index.html was updated successfully!\n\nClick 'Preview Website in Browser' to see the changes."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload screenshot:\n{e}")

    def update_html_slot(self, slot_id, filename, caption):
        if not os.path.exists(HTML_FILE):
            raise FileNotFoundError("index.html not found in the website folder.")

        with open(HTML_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Update Image src for slot
        img_pattern = rf'(<img\s+id=["\']img-slot-{slot_id}["\'][^>]*src=["\'])[^"\']*(["\'])'
        if re.search(img_pattern, content):
            content = re.sub(img_pattern, rf'\g<1>{filename}\g<2>', content)
        else:
            # Fallback pattern
            content = re.sub(rf'screenshot{slot_id}\.(png|jpg|jpeg|webp)', filename, content)

        # Update Caption for slot
        if caption:
            caption_pattern = rf'(<span\s+id=["\']caption-slot-{slot_id}["\'][^>]*>)[^<]*(</span>)'
            if re.search(caption_pattern, content):
                content = re.sub(caption_pattern, rf'\g<1>{caption}\g<2>', content)

        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(content)

    def preview_website(self):
        if os.path.exists(HTML_FILE):
            webbrowser.open(f"file://{os.path.abspath(HTML_FILE)}")
            self.status_lbl.config(text="Opening website in default browser...", fg=self.col_accent)
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
                messagebox.showinfo("ZIP Created", f"Successfully generated:\n{os.path.basename(ZIP_FILE)}\n\nReady to upload to Cloudflare Pages!")
                self.status_lbl.config(text="Cloudflare ZIP archive refreshed.", fg="#34d399")
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"Failed to create ZIP archive:\n{e}")

if __name__ == "__main__":
    app = WebsiteManagerApp()
    app.mainloop()
