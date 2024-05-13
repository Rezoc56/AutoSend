import tkinter as tk
from tkinter import messagebox, ttk
import keyboard
import os
import requests

ver = '1.2'

class AutoSend:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoSend")

        self.root.tk_setPalette(background='#222', foreground='white', activeForeground='white')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#222', foreground='white')

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x = (screen_width - width) // 2 - 90
        y = (screen_height - height) // 2 - 40

        root.geometry(f"+{x}+{y}")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, anchor="e")

        self.version_label = tk.Label(self.root, text=f"Версия: {ver}")
        self.version_label.pack(side="left", anchor="sw")

        self.version2_label = tk.Label(self.root, text="||  Послед. версия: ошибка проверки.")
        self.version2_label.pack(side="left", anchor="sw")

        self.check_update()

        self.text_entry = tk.Text(self.main_frame, height=5, width=40, bg='#333', fg='white')
        self.text_entry.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.key_label = tk.Label(self.main_frame, text="Клавиша активации:", bg='#222', fg='white')
        self.key_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.selected_key = tk.StringVar()
        self.key_button = tk.Button(self.main_frame, textvariable=self.selected_key, command=self.select_key, bg='#333', fg='white')
        self.key_button.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.key_button.config(cursor="hand2")

        self.reset_button = tk.Button(self.main_frame, text="Сбросить клавишу", command=self.reset_key, bg='#333', fg='white')
        self.reset_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.reset_button.config(cursor="hand2")

        self.start_button = tk.Button(self.main_frame, text="Запустить", command=self.start_script, bg='#333', fg='white')
        self.start_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.start_button.config(cursor="hand2")

        self.rezoc_label = tk.Label(self.root, text="Rezoc Studio")
        self.rezoc_label.pack(side="right", anchor="se")

        self.settings_path = os.path.join(os.getenv("APPDATA"), "Rezoc Studio", "AutoSend")
        self.settings_file = os.path.join(self.settings_path, "settings.txt")
        self.load_settings()

    def save_settings(self):
        with open(self.settings_file, "w") as file:
            file.write(self.selected_key.get() + "\n")
            file.write(self.text_entry.get("1.0", tk.END) + "\n")
            file.write("Здесь храняться настройки программы - клавиша которую вы выбрали и ведённый текст.")

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            os.makedirs(self.settings_path, exist_ok=True)
            self.selected_key.set("Выберите клавишу")
            self.save_settings()
        else:
            with open(self.settings_file, "r") as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    self.selected_key.set(lines[0].strip())
                    self.text_entry.insert(tk.END, lines[1])

    def select_key(self):
        self.text_entry.config(state=tk.DISABLED)
        def on_key_press(event):
            self.selected_key.set(event.name)
            self.key_button.config(state=tk.DISABLED)
            self.text_entry.config(state=tk.NORMAL)
            keyboard.unhook_all()
        keyboard.on_press(on_key_press)

    def reset_key(self):
        self.key_button.config(state=tk.NORMAL)
        self.key_button.config(cursor="hand2")
        self.selected_key.set("Выберите клавишу")

    def start_script(self):
        selected_key = self.selected_key.get()
        if selected_key == "Выберите клавишу":
            messagebox.showerror("Ошибка", "Пожалуйста, выберите клавишу")
            return
        
        self.text_entry.config(state=tk.DISABLED)
        self.key_button.config(state=tk.DISABLED, cursor="arrow")
        self.reset_button.config(state=tk.DISABLED, cursor="arrow")
        
        self.start_button.config(text="Остановить", command=self.stop_script)
        self.save_settings()
        additional_text = self.text_entry.get("1.0", tk.END)
        def on_key_press(event):
            if event.name == selected_key:
                keyboard.write(additional_text)
        keyboard.on_press(on_key_press)

    def stop_script(self):
        self.text_entry.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL, cursor="hand2")
        
        self.start_button.config(text="Запустить", command=self.start_script)
        keyboard.unhook_all()

    def check_update(self):
        try:
            version_file_url = "https://raw.githubusercontent.com/Rezoc56/AutoSend/main/version.txt"
            response = requests.get(version_file_url)

            if response.status_code == 200:
                latest_version = response.text.strip()

                current_version = ver
                if current_version != latest_version:
                    self.version_label.config(text="Версия: " + current_version)
                    self.version2_label.config(text="||  Послед. версия: " + latest_version)
                    update_button = tk.Button(self.root, text="Обновить", command=self.update_app, bg='#333', fg='white')
                    update_button.pack(side="left", anchor="s")
                    update_button.config(cursor="hand2")
                    self.latest_version = latest_version
                else:
                    self.version_label.config(text="Версия: " + current_version)
                    self.version2_label.config(text="||  Послед. версия: " + latest_version)
            else:
                print("Ошибка при загрузке версии:", response.status_code)
                messagebox.showerror("Ошибка", f"Не удалось проверить обновления: {response.status_code}")
        except Exception as e:
            print("Ошибка при проверке обновлений:", e)
            messagebox.showerror("Ошибка", f"Ошибка при проверке обновлений: {e}")

    def update_app(self):
        import webbrowser
        webbrowser.open("https://rezoc.rf.gd/autosend.php")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoSend(root)
    root.mainloop()
