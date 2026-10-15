"""
Main UI Window using Tkinter
"""

import logging
import threading
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger(__name__)

class MainWindow:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.root.title("FF Gaming Assistant Panel")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0f0f0f")
        
        self.colors = {
            "bg": "#0f0f0f",
            "card": "#1a1a1a",
            "red": "#e94560",
            "blue": "#0f3460",
            "text": "#ffffff",
            "subtext": "#a0a0a0"
        }
        
        self._setup_ui()
        self._check_status_async()

    def _setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill="both", expand=True)
        
        # Sidebar
        sidebar = tk.Frame(main_frame, bg="#121212", width=200)
        sidebar.pack(side="left", fill="y")
        
        tk.Label(sidebar, text="FF ASSISTANT", font=("Segoe UI", 14, "bold"), fg=self.colors["red"], bg="#121212").pack(pady=20)
        
        nav_items = ["Dashboard", "BlueStacks", "Key Bindings", "Settings"]
        for item in nav_items:
            btn = tk.Button(
                sidebar, text=item, anchor="w", bg="#121212", fg=self.colors["text"],
                relief="flat", font=("Segoe UI", 10), activebackground=self.colors["blue"],
                command=lambda i=item: self._navigate(i)
            )
            btn.pack(fill="x", padx=10, pady=2)
            if item == "Dashboard":
                btn.config(bg=self.colors["blue"])

        # Content
        self.content_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        self._show_dashboard()

    def _navigate(self, section):
        """Handle navigation between pages."""
        # Update sidebar active state
        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame):
                for sub_child in child.winfo_children():
                    if isinstance(sub_child, tk.Frame): # Sidebar frame
                        for btn in sub_child.winfo_children():
                            if isinstance(btn, tk.Button):
                                if btn.cget("text") == section:
                                    btn.config(bg=self.colors["blue"])
                                else:
                                    btn.config(bg="#121212")
        
        # Show correct page
        if section == "Dashboard":
            self._show_dashboard()
        elif section == "BlueStacks":
            self._show_bluestacks()
        elif section == "Key Bindings":
            self._show_keybindings()
        elif section == "Settings":
            self._show_settings()

    def _show_dashboard(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
            
        tk.Label(self.content_frame, text="Welcome to FF Gaming Assistant", font=("Segoe UI", 20, "bold"), fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=30)
        
        status_card = tk.Frame(self.content_frame, bg=self.colors["card"], width=300, height=150)
        status_card.pack(pady=20)
        status_card.pack_propagate(False)
        
        tk.Label(status_card, text="BLUESTACKS STATUS", font=("Segoe UI", 10, "bold"), fg=self.colors["red"], bg=self.colors["card"]).pack(pady=10)
        self.status_label = tk.Label(status_card, text="Checking...", font=("Segoe UI", 14, "bold"), fg=self.colors["text"], bg=self.colors["card"])
        self.status_label.pack()
        
        tk.Button(status_card, text="Launch BlueStacks", bg=self.colors["blue"], fg="white", relief="flat", command=self._launch_bs).pack(pady=10)

    def _show_bluestacks(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        
        tk.Label(self.content_frame, text="BlueStacks Manager", font=("Segoe UI", 16, "bold"), fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=20)
        
        frame = tk.Frame(self.content_frame, bg=self.colors["card"])
        frame.pack(fill="both", expand=True, padx=20)
        
        tk.Label(frame, text="TROUBLESHOOTING", font=("Segoe UI", 10, "bold"), fg=self.colors["red"], bg=self.colors["card"]).pack(pady=10, anchor="w")
        instructions = [
            "1. Ensure Hyper-V is enabled in BIOS for best performance.",
            "2. If BlueStacks is laggy, check 'Game Mode' in Windows Settings.",
            "3. Assign more RAM to the emulator in BlueStacks Settings > Performance."
        ]
        for inst in instructions:
            tk.Label(frame, text=inst, fg=self.colors["text"], font=("Segoe UI", 10), anchor="w", bg=self.colors["card"]).pack(pady=5, padx=10)

    def _show_keybindings(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        
        tk.Label(self.content_frame, text="Recommended Key Bindings", font=("Segoe UI", 16, "bold"), fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=20)
        
        frame = tk.Frame(self.content_frame, bg=self.colors["card"])
        frame.pack(fill="both", expand=True, padx=20)
        
        bindings = self.app.get_config("key_bindings", {})
        if not bindings:
            bindings = {"Forward": "W", "Backward": "S", "Left": "A", "Right": "D", "Fire": "LMB", "Aim": "RMB", "Reload": "R"}
            
        for key, val in bindings.items():
            row = tk.Frame(frame, bg=self.colors["card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=key, width=20, anchor="w", fg=self.colors["text"], font=("Segoe UI", 10), bg=self.colors["card"]).pack(side="left")
            tk.Label(row, text=val, width=20, anchor="e", fg=self.colors["red"], font=("Segoe UI", 10, "bold"), bg=self.colors["card"]).pack(side="right")

    def _show_settings(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        
        tk.Label(self.content_frame, text="Settings", font=("Segoe UI", 16, "bold"), fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=20)
        tk.Label(self.content_frame, text="Configuration is saved automatically to ~/.ff_gaming_panel/config.json", fg=self.colors["subtext"], bg=self.colors["bg"]).pack()

    def _check_status_async(self):
        """Check BlueStacks status in a background thread."""
        def check():
            from src.modules.bluestacks import BlueStacksManager
            manager = BlueStacksManager()
            status = manager.get_status()
            
            def update_ui():
                if hasattr(self, 'status_label'):
                    if status["running"]:
                        self.status_label.config(text="RUNNING", fg="#00ff00")
                    elif status["installed"]:
                        self.status_label.config(text="INSTALLED", fg="#ffff00")
                    else:
                        self.status_label.config(text="NOT FOUND", fg="#ff0000")
            
            self.root.after(0, update_ui)
            
        threading.Thread(target=check, daemon=True).start()

    def _launch_bs(self):
        from src.modules.bluestacks import BlueStacksManager
        manager = BlueStacksManager()
        result = manager.launch_bluestacks()
        if result["success"]:
            messagebox.showinfo("Success", "BlueStacks Launching...")
        else:
            messagebox.showwarning("Failed", result["message"])

    def mainloop(self):
        self.root.mainloop()