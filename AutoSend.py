import tkinter as tk
from tkinter import messagebox, ttk
import keyboard
import os
import requests
import threading
import time

ver = '1.4'

class AutoSend:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoSend")
        self.root.resizable(False, False)
        self.root.attributes('-fullscreen', False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._build_styles()
        self._center_window()
        self._build_ui()
        self._bind_hotkeys()

        self.settings_path = os.path.join(os.getenv("APPDATA"), "Rezoc Studio", "AutoSend")
        self.settings_file = os.path.join(self.settings_path, "settings.txt")
        self.load_settings()

        threading.Thread(target=self.check_update, daemon=True).start()

    BG     = '#1e1e1e'
    BG2    = '#2a2a2a'
    BG3    = '#333333'
    ACCENT = '#4a9eff'
    FG     = '#e0e0e0'
    FG_DIM = '#888888'
    GREEN  = '#4caf50'
    RED    = '#f44336'
    ORANGE = '#ff9800'

    def _build_styles(self):
        self.root.configure(bg=self.BG)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background=self.BG, foreground=self.FG)
        style.configure('TScale', background=self.BG, troughcolor=self.BG3, slidercolor=self.ACCENT)

    def _center_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-420)//2}+{(sh-380)//2}")

    def _build_ui(self):
        self.status_frame = tk.Frame(self.root, bg=self.BG3, height=4)
        self.status_frame.pack(fill='x', side='top')

        self.main_frame = tk.Frame(self.root, bg=self.BG)
        self.main_frame.pack(padx=14, pady=(12, 6), fill='both')

        text_header = tk.Frame(self.main_frame, bg=self.BG)
        text_header.pack(fill='x')
        tk.Label(text_header, text="Текст для отправки", bg=self.BG, fg=self.FG_DIM, font=('Segoe UI', 8)).pack(side='left')
        self.char_count_label = tk.Label(text_header, text="0 симв.", bg=self.BG, fg=self.FG_DIM, font=('Segoe UI', 8))
        self.char_count_label.pack(side='right')

        text_frame = tk.Frame(self.main_frame, bg=self.ACCENT, padx=1, pady=1)
        text_frame.pack(fill='x', pady=(3, 8))
        self.text_entry = tk.Text(
            text_frame, height=5, width=44, bg=self.BG2, fg=self.FG,
            insertbackground=self.ACCENT, selectbackground=self.ACCENT, selectforeground='white',
            relief='flat', font=('Segoe UI', 10), wrap='word', undo=True
        )
        self.text_entry.pack(fill='both')
        self.text_entry.bind('<KeyRelease>', self._update_char_count)

        self._build_context_menu()
        tk.Frame(self.main_frame, bg=self.BG3, height=1).pack(fill='x', pady=4)

        key_row = tk.Frame(self.main_frame, bg=self.BG)
        key_row.pack(fill='x', pady=4)
        tk.Label(key_row, text="Клавиша активации:", bg=self.BG, fg=self.FG, font=('Segoe UI', 9)).pack(side='left')
        self.selected_key = tk.StringVar()
        self.key_button = tk.Button(key_row, textvariable=self.selected_key, command=self.select_key,
            bg=self.BG3, fg=self.ACCENT, activebackground='#3a3a3a', activeforeground=self.ACCENT,
            relief='flat', font=('Segoe UI', 9, 'bold'), cursor='hand2', padx=8, pady=2)
        self.key_button.pack(side='left', padx=8)
        self.reset_button = tk.Button(key_row, text="x Сбросить", command=self.reset_key,
            bg=self.BG3, fg=self.FG_DIM, activebackground='#3a3a3a', activeforeground=self.FG,
            relief='flat', font=('Segoe UI', 8), cursor='hand2', padx=6, pady=2)
        self.reset_button.pack(side='right')

        delay_row = tk.Frame(self.main_frame, bg=self.BG)
        delay_row.pack(fill='x', pady=4)
        tk.Label(delay_row, text="Задержка перед отправкой:", bg=self.BG, fg=self.FG, font=('Segoe UI', 9)).pack(side='left')
        self.delay_var = tk.DoubleVar(value=0.0)
        self.delay_label = tk.Label(delay_row, text="0.0 с", bg=self.BG, fg=self.ACCENT, font=('Segoe UI', 9, 'bold'), width=5)
        self.delay_label.pack(side='right')
        self.delay_scale = ttk.Scale(delay_row, from_=0.0, to=5.0, variable=self.delay_var,
            orient='horizontal', command=self._update_delay_label, length=140)
        self.delay_scale.pack(side='right', padx=4)

        tk.Frame(self.main_frame, bg=self.BG3, height=1).pack(fill='x', pady=4)
        self.start_button = tk.Button(self.main_frame, text="Запустить", command=self.start_script,
            bg=self.GREEN, fg='white', activebackground='#45a049', activeforeground='white',
            relief='flat', font=('Segoe UI', 10, 'bold'), cursor='hand2', pady=6)
        self.start_button.pack(fill='x', pady=(4, 0))
        tk.Label(self.main_frame, text="Ctrl+Enter — запустить/остановить", bg=self.BG, fg=self.FG_DIM, font=('Segoe UI', 7)).pack(anchor='e')

        mode_row = tk.Frame(self.main_frame, bg=self.BG)
        mode_row.pack(fill='x', pady=(6, 0))
        tk.Label(mode_row, text="Режим отправки:", bg=self.BG, fg=self.FG, font=('Segoe UI', 9)).pack(side='left')
        self.send_mode = tk.StringVar(value="enter")
        tk.Radiobutton(mode_row, text="Вставка + Enter", variable=self.send_mode, value="enter",
            bg=self.BG, fg=self.FG, selectcolor=self.BG3, activebackground=self.BG,
            activeforeground=self.FG, font=('Segoe UI', 9)).pack(side='left', padx=(8,4))
        tk.Radiobutton(mode_row, text="Только вставка", variable=self.send_mode, value="paste",
            bg=self.BG, fg=self.FG, selectcolor=self.BG3, activebackground=self.BG,
            activeforeground=self.FG, font=('Segoe UI', 9)).pack(side='left')

        bottom = tk.Frame(self.root, bg=self.BG2)
        bottom.pack(fill='x', side='bottom')
        self.version_label = tk.Label(bottom, text=f"v{ver}", bg=self.BG2, fg=self.FG_DIM, font=('Segoe UI', 8))
        self.version_label.pack(side='left', padx=8, pady=4)
        self.version2_label = tk.Label(bottom, text="Проверка обновлений...", bg=self.BG2, fg=self.FG_DIM, font=('Segoe UI', 8))
        self.version2_label.pack(side='left', pady=4)
        self.status_label = tk.Label(bottom, text="* Остановлено", bg=self.BG2, fg=self.FG_DIM, font=('Segoe UI', 8))
        self.status_label.pack(side='right', padx=8, pady=4)
        tk.Label(bottom, text="Rezoc Studio", bg=self.BG2, fg=self.FG_DIM, font=('Segoe UI', 8)).pack(side='right', padx=4, pady=4)

    def _build_context_menu(self):
        self.context_menu = tk.Menu(self.text_entry, tearoff=0, bg=self.BG3, fg=self.FG,
            activebackground=self.ACCENT, activeforeground='white')
        self.context_menu.add_command(label="Вырезать",    command=self._cut)
        self.context_menu.add_command(label="Копировать",  command=self._copy)
        self.context_menu.add_command(label="Вставить",    command=self._paste)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выбрать всё", command=self._select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Отменить",    command=lambda: self.text_entry.edit_undo())
        self.context_menu.add_command(label="Повторить",   command=lambda: self.text_entry.edit_redo())
        self.text_entry.bind("<Button-3>", self._show_context_menu)

    def _bind_hotkeys(self):
        e = self.text_entry
        e.bind('<Control-c>', lambda ev: (e.event_generate('<<Copy>>'), 'break'))
        e.bind('<Control-x>', lambda ev: (e.event_generate('<<Cut>>'), 'break'))
        e.bind('<Control-v>', lambda ev: (e.event_generate('<<Paste>>'), 'break'))
        e.bind('<Control-a>', lambda ev: self._select_all_return())
        e.bind('<Control-z>', lambda ev: (e.edit_undo(), 'break'))
        e.bind('<Control-y>', lambda ev: (e.edit_redo(), 'break'))
        e.bind('<Control-Return>', lambda ev: self._toggle_script())
        self.root.bind('<Control-Return>', lambda ev: self._toggle_script())

    def _update_char_count(self, event=None):
        n = len(self.text_entry.get('1.0', 'end-1c'))
        self.char_count_label.config(text=f"{n} симв.", fg=self.ORANGE if n > 500 else self.FG_DIM)

    def _update_delay_label(self, val=None):
        self.delay_label.config(text=f"{float(self.delay_var.get()):.1f} с")

    def _set_status(self, running):
        if running:
            self.status_label.config(text="* Активно", fg=self.GREEN)
            self.status_frame.config(bg=self.GREEN)
        else:
            self.status_label.config(text="* Остановлено", fg=self.FG_DIM)
            self.status_frame.config(bg=self.BG3)

    def _toggle_script(self):
        if 'Запустить' in self.start_button.cget('text'):
            self.start_script()
        else:
            self.stop_script()

    def _select_all(self):
        self.text_entry.tag_add(tk.SEL, '1.0', tk.END)
        self.text_entry.mark_set(tk.INSERT, '1.0')
        self.text_entry.see(tk.INSERT)

    def _select_all_return(self):
        self._select_all()
        return 'break'

    def _cut(self):   self.text_entry.event_generate('<<Cut>>')
    def _copy(self):  self.text_entry.event_generate('<<Copy>>')
    def _paste(self): self.text_entry.event_generate('<<Paste>>')

    def _show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def select_key(self):
        self.key_button.config(text="Нажмите клавишу...", state=tk.DISABLED, fg=self.ORANGE)
        self.text_entry.config(state=tk.DISABLED)
        self.root.focus_set()
        def on_key_press(event):
            self.selected_key.set(event.name)
            self.key_button.config(state=tk.NORMAL, fg=self.ACCENT)
            self.root.after(100, lambda: self.text_entry.config(state=tk.NORMAL))
            keyboard.unhook_all()
        keyboard.on_press(on_key_press)

    def reset_key(self):
        self.key_button.config(state=tk.NORMAL, cursor='hand2', fg=self.ACCENT)
        self.selected_key.set("Выберите клавишу")

    def start_script(self):
        selected_key = self.selected_key.get()
        if selected_key in ("Выберите клавишу", ""):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите клавишу")
            return
        self.text_entry.config(state=tk.DISABLED)
        self.key_button.config(state=tk.DISABLED, cursor='arrow')
        self.reset_button.config(state=tk.DISABLED, cursor='arrow')
        self.delay_scale.config(state=tk.DISABLED)
        self.start_button.config(text="Остановить", command=self.stop_script,
            bg=self.RED, activebackground='#d32f2f')
        self._set_status(True)

        additional_text = self.text_entry.get('1.0', tk.END).rstrip('\n')
        delay = float(self.delay_var.get())

        send_mode = self.send_mode.get()
        def on_key_press(event):
            if event.name == selected_key:
                if delay > 0:
                    time.sleep(delay)
                keyboard.write(additional_text)
                if send_mode == "enter":
                    keyboard.press_and_release('enter')

        keyboard.on_press(on_key_press)

    def stop_script(self):
        keyboard.unhook_all()
        self.text_entry.config(state=tk.NORMAL)
        self.key_button.config(state=tk.NORMAL, cursor='hand2')
        self.reset_button.config(state=tk.NORMAL, cursor='hand2')
        self.delay_scale.config(state=tk.NORMAL)
        self.start_button.config(text="Запустить", command=self.start_script,
            bg=self.GREEN, activebackground='#45a049')
        self._set_status(False)

    def on_closing(self):
        self.save_settings()
        self.root.destroy()

    def save_settings(self):
        os.makedirs(self.settings_path, exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            f.write(self.selected_key.get() + '\n')
            f.write(self.text_entry.get('1.0', tk.END).rstrip('\n') + '\n')
            f.write(f'{self.delay_var.get():.1f}\n')
            f.write(self.send_mode.get() + '\n')
            f.write('Здесь хранятся настройки программы.')

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            os.makedirs(self.settings_path, exist_ok=True)
            self.selected_key.set('Выберите клавишу')
        else:
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if lines: self.selected_key.set(lines[0].strip())
                if len(lines) >= 2:
                    self.text_entry.insert(tk.END, lines[1].strip())
                    self._update_char_count()
                if len(lines) >= 3:
                    try: self.delay_var.set(float(lines[2].strip())); self._update_delay_label()
                    except ValueError: pass
                if len(lines) >= 4:
                    mode = lines[3].strip()
                    if mode in ("enter", "paste"):
                        self.send_mode.set(mode)
            except Exception:
                self.selected_key.set('Выберите клавишу')

    def check_update(self):
        try:
            r = requests.get('https://raw.githubusercontent.com/Rezoc56/AutoSend/main/version.txt', timeout=5)
            if r.status_code == 200:
                latest = r.text.strip()
                if ver != latest:
                    self.root.after(0, lambda: self._show_update_available(latest))
                else:
                    self.root.after(0, lambda: self.version2_label.config(text="[ok] Актуальная", fg=self.GREEN))
            else:
                self.root.after(0, lambda: self.version2_label.config(text='Ошибка проверки', fg=self.ORANGE))
        except Exception:
            self.root.after(0, lambda: self.version2_label.config(text='Нет соединения', fg=self.FG_DIM))

    def _show_update_available(self, latest):
        self.version2_label.config(text=f"-> Доступна v{latest}", fg=self.ORANGE)
        tk.Button(self.root, text="Обновить", command=self.update_app,
            bg=self.ORANGE, fg='white', activebackground='#e68900',
            relief='flat', font=('Segoe UI', 8, 'bold'), cursor='hand2', padx=6, pady=2
        ).pack(side='left', anchor='s', padx=4, pady=4)

    def update_app(self):
        import webbrowser
        webbrowser.open('https://rezoc.fun/autosend.php')


if __name__ == '__main__':
    root = tk.Tk()
    app = AutoSend(root)
    root.mainloop()
