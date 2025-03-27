import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from tkinter.messagebox import showerror
import whisper
import torch
import threading
import sys
import queue
import os
import csv

class RedirectStdout:
    def __init__(self, queue):
        self.queue = queue
    
    def write(self, text):
        self.queue.put(text)
    
    def flush(self):
        pass

class WhisperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SWIP (Simple Whisper Interface Panel)")

        # Проверка доступности CUDA
        self.cuda_available = torch.cuda.is_available()
        
        # Инициализируем переменные ДО создания виджетов
        self.save_txt = tk.BooleanVar(value=True)
        self.save_tsv = tk.BooleanVar(value=False)
        self.use_cuda = tk.BooleanVar(value=self.cuda_available)
		
        self.output_queue = queue.Queue()
        self.system_queue = queue.Queue()  # Отдельная очередь для системных сообщений
        self.create_widgets()
        self.root.after(100, self.process_output_queue)
        
    def create_widgets(self):
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)
        
        # Кнопка выбора файла
        self.btn_file = ttk.Button(
            control_frame, 
            text="Выбрать файл",
            command=self.select_file
        )
        self.btn_file.pack(side=tk.LEFT, padx=5)
        
        # Выбор модели
        model_frame = ttk.Frame(control_frame)
        model_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(model_frame, text="Модель:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value="turbo")
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large", "turbo"],
            state="readonly",
            width=10
        )
        self.model_combo.pack(side=tk.LEFT, padx=5)

        # Выбор языка
        lang_frame = ttk.Frame(control_frame)
        lang_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(lang_frame, text="Язык:").pack(side=tk.LEFT)
        self.language = tk.StringVar(value="None")
        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language,
            values=["None","Belarusian","Chinese","Danish","Dutch","English","French","German","Greek","Italian","Japanese","Latin","Russian","Serbian","Spanish","Swedish"],
            state="readonly",
            width=10
        )
        self.lang_combo.pack(side=tk.LEFT, padx=5)
        
        # Настройки сохранения
        save_frame = ttk.Frame(control_frame)
        save_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(save_frame, text="Сохранить как:").pack(side=tk.LEFT)
        ttk.Checkbutton(
            save_frame, 
            text="TXT", 
            variable=self.save_txt
        ).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(
            save_frame, 
            text="TSV", 
            variable=self.save_tsv
        ).pack(side=tk.LEFT, padx=2)
        # Чекбокс для CUDA
        cuda_frame = ttk.Frame(control_frame)
        cuda_frame.pack(side=tk.LEFT, padx=10)
        
        self.cuda_check = ttk.Checkbutton(
            cuda_frame,
            text="Использовать GPU",
            variable=self.use_cuda,
            state="normal" if self.cuda_available else "disabled"
        )
        self.cuda_check.pack(side=tk.LEFT)
        if not self.cuda_available: 
            ToolTip(cuda_frame, "CUDA недоступна: GPU не обнаружен")
        
        # Кнопка запуска
        self.btn_start = ttk.Button(
            control_frame,
            text="Старт",
            command=self.start_processing,
            state=tk.DISABLED
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        # Текстовое поле вывода
        self.output_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10)
        )
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Медиа файлы", "*.mp4 *.avi *.mkv *.mp3 *.wav"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            self.file_path = file_path
            self.btn_start.config(state=tk.NORMAL)
            self.output_area.delete(1.0, tk.END)
            self.system_queue.put(f"Выбран файл: {file_path}")
            
    def start_processing(self):
        self.btn_start.config(state=tk.DISABLED)
        self.system_queue.put(f"Начата обработка...")
        
        threading.Thread(
            target=self.process_file,
            args=(self.file_path, self.model_var.get()),
            daemon=True
        ).start()
    
    def process_file(self, file_path, model_size):
        original_stdout = sys.stdout
        sys.stdout = RedirectStdout(self.output_queue)
        
        try:
            device = "cuda" if self.use_cuda.get() and self.cuda_available else "cpu"
            model = whisper.load_model(model_size, device=device, in_memory=True)
            result = model.transcribe(
                file_path,
                verbose=True,
                fp16=(device == "cuda"),  # FP16 только для CUDA
                temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.5,
                language=self.language.get()
            )

            # Автосохранение результатов
            if self.save_txt.get() or self.save_tsv.get():
                self.root.after(0, lambda: self.save_results(result, file_path))
            
        except Exception as e:
            # Обработка ошибок CUDA
            if "CUDA" in str(e):
                self.root.after(0, lambda: self.print_output(
                    "\nОшибка CUDA: Переключаюсь на CPU. Убедитесь, что:\n"
                    "1. У вас NVIDIA GPU\n"
                    "2. Установлены драйверы CUDA 11.8+\n"
                    "3. PyTorch собран с поддержкой CUDA",
                tag="system"))
                device = "cpu"
                model = whisper.load_model(model_size, device=device)
                result = model.transcribe(file_path, verbose=True)

            self.root.after(0, lambda: showerror("Ошибка", str(e)))
        finally:
            sys.stdout = original_stdout
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
            if self.use_cuda.get():
                torch.cuda.empty_cache()
    
    def save_results(self, result, input_path):
        """Сохранение результатов в выбранных форматах"""
        base_name = os.path.splitext(input_path)[0]
        segments = result.get("segments", [])

        # TXT
        if self.save_txt.get() and segments:
            txt_path = f"{base_name}_{self.model_var.get()}.txt"
            try:
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(result["text"])
                self.system_queue.put(f"\nСохранено TXT: {txt_path}")
            except Exception as e:
                self.system_queue.put(f"\nОшибка сохранения TXT: {str(e)}")
        
        # TSV
        if self.save_tsv.get() and segments:
            tsv_path = f"{base_name}_{self.model_var.get()}.tsv"
            try:
                with open(tsv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f, delimiter="\t")
                    writer.writerow(["Start", "End", "Text"])
                    for seg in segments:
                        writer.writerow([
                            round(seg["start"], 2),
                            round(seg["end"], 2),
                            seg["text"].strip()
                        ])
                self.system_queue.put(f"\nСохранено TSV: {tsv_path}",)
            except Exception as e:
                self.system_queue.put(f"\nОшибка сохранения TSV: {str(e)}")

        # Форсируем вывод после добавления в очередь
        self.root.after(50, self.process_output_queue)
    
    def process_output_queue(self):
        # Обрабатываем сначала очередь Whisper
        while not self.output_queue.empty():
            msg = self.output_queue.get_nowait()
            self.print_output(msg,end="")
        
        # Затем системные сообщения
        while not self.system_queue.empty():
            msg = self.system_queue.get_nowait()
            self.print_output(msg,tag="system")
        
        self.root.after(100, self.process_output_queue)
        if not self.system_queue.empty():
            self.output_area.see(tk.END)

    
    def print_output(self, text, tag="", end="\n"):
        if tag == "system":
            self.output_area.tag_config("system", foreground="blue")
        self.output_area.insert(tk.END, text + end,tag)
        self.output_area.see(tk.END)
        self.output_area.update_idletasks()

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(
            self.tip,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1
        )
        label.pack()

    def hide(self, event=None):
        if hasattr(self, "tip"):
            self.tip.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()