import tkinter as tk
from tkinter import messagebox, ttk
import json
import keyboard
import os
import random
import requests
import threading
import time

ver = '1.5'

class AutoSend:
    TOGGLE_HOTKEY = 'f8'

    def __init__(self, root):
        self.root = root
        self.root.title("AutoSend")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.running = False
        self._hook = None
        self._capture_hook = None
        self._sent = 0
        self._index = 0

        self._build_styles()
        self._build_ui()
        self._bind_hotkeys()
        self._center_window()

        self.settings_path = os.path.join(os.getenv("APPDATA"), "Rezoc Studio", "AutoSend")
        self.settings_file = os.path.join(self.settings_path, "settings.json")
        self.load_settings()

        keyboard.add_hotkey(self.TOGGLE_HOTKEY, lambda: self.root.after(0, self._toggle_script))
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
    BG_HOVER = '#404040'

    def _build_styles(self):
        self.root.configure(bg=self.BG)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background=self.BG, foreground=self.FG)
        style.configure('TScale', background=self.BG, troughcolor=self.BG3, slidercolor=self.ACCENT)

    def _label(self, parent, text, dim=False, size=9, bold=False, **kw):
        kw.setdefault('bg', self.BG)
        kw.setdefault('fg', self.FG_DIM if dim else self.FG)
        return tk.Label(parent, text=text, font=('Segoe UI', size, 'bold' if bold else 'normal'), **kw)

    def _button(self, parent, text, command, bg=None, fg=None, hover=None, size=9, bold=False, **kw):
        btn = tk.Button(parent, text=text, command=command, relief='flat', bd=0, cursor='hand2',
                        font=('Segoe UI', size, 'bold' if bold else 'normal'), **kw)
        btn.bind('<Enter>', lambda e: btn['state'] == 'normal' and btn.config(bg=btn.hover_bg))
        btn.bind('<Leave>', lambda e: btn['state'] == 'normal' and btn.config(bg=btn.base_bg))
        self._restyle(btn, bg or self.BG3, hover or self.BG_HOVER, fg or self.FG)
        return btn

    def _restyle(self, btn, bg, hover, fg=None):
        btn.base_bg, btn.hover_bg = bg, hover
        btn.config(bg=bg, activebackground=hover)
        if fg:
            btn.config(fg=fg, activeforeground=fg)

    def _toggle_widget(self, cls, parent, text, **kw):
        return cls(parent, text=text, bg=self.BG, fg=self.FG, selectcolor=self.BG3,
                   activebackground=self.BG, activeforeground=self.FG, bd=0,
                   highlightthickness=0, cursor='hand2', font=('Segoe UI', 9), **kw)

    def _row(self, pady=4):
        row = tk.Frame(self.main_frame, bg=self.BG)
        row.pack(fill='x', pady=pady)
        return row

    def _divider(self):
        tk.Frame(self.main_frame, bg=self.BG3, height=1).pack(fill='x', pady=6)

    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build_ui(self):
        self.status_frame = tk.Frame(self.root, bg=self.BG3, height=3)
        self.status_frame.pack(fill='x', side='top')

        self.main_frame = tk.Frame(self.root, bg=self.BG)
        self.main_frame.pack(padx=16, pady=(12, 6), fill='both')

        # --- Текст ---
        header = tk.Frame(self.main_frame, bg=self.BG)
        header.pack(fill='x')
        self._label(header, "Текст для отправки", dim=True, size=8).pack(side='left')
        self.char_count_label = self._label(header, "0 симв.", dim=True, size=8)
        self.char_count_label.pack(side='right')

        text_frame = tk.Frame(self.main_frame, bg=self.ACCENT, padx=1, pady=1)
        text_frame.pack(fill='x', pady=(3, 4))
        self.text_entry = tk.Text(
            text_frame, height=5, width=46, bg=self.BG2, fg=self.FG,
            insertbackground=self.ACCENT, selectbackground=self.ACCENT, selectforeground='white',
            relief='flat', font=('Segoe UI', 10), wrap='word', undo=True, padx=6, pady=4
        )
        self.text_entry.pack(fill='both')
        self.text_entry.bind('<KeyRelease>', self._update_char_count)
        self._build_context_menu()
        self._divider()

        # --- Клавиша ---
        key_row = self._row()
        self._label(key_row, "Клавиша активации:").pack(side='left')
        self.selected_key = tk.StringVar()
        self.key_button = self._button(key_row, None, self.select_key, fg=self.ACCENT,
                                       bold=True, textvariable=self.selected_key, padx=10, pady=2)
        self.key_button.pack(side='left', padx=8)
        self.reset_button = self._button(key_row, "✕ Сбросить", self.reset_key,
                                         fg=self.FG_DIM, size=8, padx=6, pady=2)
        self.reset_button.pack(side='right')

        # --- Задержка ---
        delay_row = self._row()
        self._label(delay_row, "Задержка перед отправкой:").pack(side='left')
        self.delay_var = tk.DoubleVar(value=0.0)
        self.delay_label = self._label(delay_row, "0.0 с", bold=True, fg=self.ACCENT, width=5)
        self.delay_label.pack(side='right')
        self.delay_scale = ttk.Scale(delay_row, from_=0.0, to=5.0, variable=self.delay_var,
                                     orient='horizontal', command=self._update_delay_label, length=140)
        self.delay_scale.pack(side='right', padx=4)

        # --- Режимы ---
        self._divider()
        self.send_mode = tk.StringVar(value="enter")
        self.seq_var = tk.BooleanVar(value=False)
        self.humanize_var = tk.BooleanVar(value=False)
        self.topmost_var = tk.BooleanVar(value=False)

        mode_row = self._row(2)
        self._label(mode_row, "Режим отправки:").pack(side='left')
        r1 = self._toggle_widget(tk.Radiobutton, mode_row, "Текст + Enter", variable=self.send_mode, value="enter")
        r2 = self._toggle_widget(tk.Radiobutton, mode_row, "Только текст", variable=self.send_mode, value="paste")
        r1.pack(side='left', padx=(8, 4))
        r2.pack(side='left')

        opts_row = self._row(2)
        c1 = self._toggle_widget(tk.Checkbutton, opts_row, "По очереди (строка = нажатие)", variable=self.seq_var)
        c2 = self._toggle_widget(tk.Checkbutton, opts_row, "Случайность задержки", variable=self.humanize_var)
        c1.pack(side='left')
        c2.pack(side='left', padx=(8, 0))
        self._option_widgets = (r1, r2, c1, c2)

        top_row = self._row(2)
        self._toggle_widget(tk.Checkbutton, top_row, "Поверх всех окон",
                            variable=self.topmost_var, command=self._apply_topmost).pack(side='left')

        # --- Запуск ---
        self._divider()
        self.start_button = self._button(self.main_frame, "Запустить", self.start_script,
                                         bg=self.GREEN, hover='#45a049', fg='white', size=10, bold=True, pady=7)
        self.start_button.pack(fill='x', pady=(2, 0))
        self._label(self.main_frame, f"Ctrl+Enter / {self.TOGGLE_HOTKEY.upper()} — запустить/остановить",
                    dim=True, size=7).pack(anchor='e')

        # --- Нижняя панель ---
        bottom = tk.Frame(self.root, bg=self.BG2)
        bottom.pack(fill='x', side='bottom')
        self.version_label = self._label(bottom, f"v{ver}", dim=True, size=8, bg=self.BG2)
        self.version_label.pack(side='left', padx=8, pady=4)
        self.version2_label = self._label(bottom, "Проверка обновлений...", dim=True, size=8, bg=self.BG2)
        self.version2_label.pack(side='left', pady=4)
        self.status_label = self._label(bottom, "● Остановлено", dim=True, size=8, bg=self.BG2)
        self.status_label.pack(side='right', padx=8, pady=4)
        self.counter_label = self._label(bottom, "Отправлено: 0", dim=True, size=8, bg=self.BG2)
        self.counter_label.pack(side='right', padx=4, pady=4)

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
        text = self.text_entry.get('1.0', 'end-1c')
        n = len(text)
        lines = sum(1 for l in text.splitlines() if l.strip())
        self.char_count_label.config(text=f"{n} симв. · {lines} стр.",
                                     fg=self.ORANGE if n > 500 else self.FG_DIM)

    def _update_delay_label(self, val=None):
        self.delay_label.config(text=f"{float(self.delay_var.get()):.1f} с")

    def _set_status(self, running):
        self.status_label.config(text="● Активно" if running else "● Остановлено",
                                 fg=self.GREEN if running else self.FG_DIM)
        self.status_frame.config(bg=self.GREEN if running else self.BG3)

    def _toggle_script(self):
        self.stop_script() if self.running else self.start_script()

    def _update_counter(self):
        self.counter_label.config(text=f"Отправлено: {self._sent}")

    def _apply_topmost(self):
        self.root.attributes('-topmost', self.topmost_var.get())

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
        self.selected_key.set("Нажмите клавишу...")
        self.key_button.config(state=tk.DISABLED, fg=self.ORANGE)
        self.text_entry.config(state=tk.DISABLED)
        self.root.focus_set()

        def on_key_press(event):
            keyboard.unhook(self._capture_hook)
            self.root.after(0, lambda: self._finish_key_select(event.name))
        self._capture_hook = keyboard.on_press(on_key_press)

    def _finish_key_select(self, name):
        self.selected_key.set(name)
        self.key_button.config(state=tk.NORMAL, fg=self.ACCENT)
        self.text_entry.config(state=tk.NORMAL)

    def _set_controls(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        cursor = 'hand2' if enabled else 'arrow'
        self.text_entry.config(state=state)
        for b in (self.key_button, self.reset_button):
            b.config(state=state, cursor=cursor)
        self.delay_scale.config(state=state)
        for w in self._option_widgets:
            w.config(state=state)

    def reset_key(self):
        self.key_button.config(state=tk.NORMAL, cursor='hand2', fg=self.ACCENT)
        self.selected_key.set("Выберите клавишу")

    def start_script(self):
        key = self.selected_key.get()
        if key in ("Выберите клавишу", "Нажмите клавишу...", ""):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите клавишу")
            return
        text = self.text_entry.get('1.0', tk.END).rstrip('\n')
        if not text.strip():
            messagebox.showwarning("Пустой текст", "Введите текст для отправки")
            return

        messages = [l for l in text.splitlines() if l.strip()] if self.seq_var.get() else [text]
        delay = float(self.delay_var.get())
        humanize = self.humanize_var.get()
        press_enter = self.send_mode.get() == "enter"
        self._sent = self._index = 0
        self._update_counter()
        busy = threading.Lock()

        def worker():
            if not busy.acquire(blocking=False):
                return
            try:
                if delay > 0:
                    time.sleep(delay * random.uniform(0.7, 1.3) if humanize else delay)
                msg = messages[self._index % len(messages)]
                self._index += 1
                keyboard.write(msg)
                if press_enter:
                    keyboard.press_and_release('enter')
                self._sent += 1
                self.root.after(0, self._update_counter)
            finally:
                busy.release()

        def on_press(event):
            if event.name == key:
                threading.Thread(target=worker, daemon=True).start()

        self._hook = keyboard.on_press(on_press)
        self.running = True
        self._set_controls(False)
        self._restyle(self.start_button, self.RED, '#d32f2f')
        self.start_button.config(text="Остановить", command=self.stop_script)
        self._set_status(True)

    def stop_script(self):
        if self._hook:
            keyboard.unhook(self._hook)
            self._hook = None
        self.running = False
        self._set_controls(True)
        self._restyle(self.start_button, self.GREEN, '#45a049')
        self.start_button.config(text="Запустить", command=self.start_script)
        self._set_status(False)

    def on_closing(self):
        self.save_settings()
        keyboard.unhook_all()
        self.root.destroy()

    def save_settings(self):
        data = {
            "key": self.selected_key.get(),
            "text": self.text_entry.get('1.0', 'end-1c'),
            "delay": round(self.delay_var.get(), 1),
            "mode": self.send_mode.get(),
            "sequential": self.seq_var.get(),
            "humanize": self.humanize_var.get(),
            "topmost": self.topmost_var.get(),
        }
        try:
            os.makedirs(self.settings_path, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def load_settings(self):
        self.selected_key.set('Выберите клавишу')
        data = {}
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:  # миграция со старого settings.txt
                legacy = os.path.join(self.settings_path, "settings.txt")
                if os.path.exists(legacy):
                    with open(legacy, 'r', encoding='utf-8') as f:
                        l = [x.rstrip('\n') for x in f.readlines()]
                    data = {"key": l[0] if l else "", "text": l[1] if len(l) > 1 else "",
                            "delay": float(l[2]) if len(l) > 2 else 0.0,
                            "mode": l[3] if len(l) > 3 else "enter"}
        except Exception:
            data = {}

        if data.get("key"):
            self.selected_key.set(data["key"])
        self.text_entry.insert('1.0', data.get("text", ""))
        self.delay_var.set(float(data.get("delay", 0.0)))
        if data.get("mode") in ("enter", "paste"):
            self.send_mode.set(data["mode"])
        self.seq_var.set(bool(data.get("sequential", False)))
        self.humanize_var.set(bool(data.get("humanize", False)))
        self.topmost_var.set(bool(data.get("topmost", False)))
        self._update_char_count()
        self._update_delay_label()
        self._apply_topmost()

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
        webbrowser.open('https://rezocstudio.com/autosend.php')


if __name__ == '__main__':
    root = tk.Tk()
    app = AutoSend(root)
    root.mainloop()
