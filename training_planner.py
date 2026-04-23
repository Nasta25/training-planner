import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = "trainings.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")
        
        # Данные: список словарей
        self.trainings = []
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        self.refresh_table()
    
    def create_widgets(self):
        # Рамка для ввода
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку")
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5, pady=5)
        self.type_combo = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Велосипед", "Силовая", "Йога"], width=15)
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5, pady=5)
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавить
        add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.pack(pady=5, padx=10, fill="x")
        
        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_type_combo = ttk.Combobox(filter_frame, values=["Все", "Бег", "Плавание", "Велосипед", "Силовая", "Йога"], width=15)
        self.filter_type_combo.set("Все")
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_btn.grid(row=0, column=4, padx=5, pady=5)
        
        reset_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        reset_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Таблица для отображения тренировок
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)
        
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def validate_date(self, date_str):
        """Проверка формата даты ГГГГ-ММ-ДД"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def add_training(self):
        date = self.date_entry.get().strip()
        training_type = self.type_combo.get()
        duration = self.duration_entry.get().strip()
        
        # Проверки
        if not date or not training_type or not duration:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        try:
            duration_val = float(duration)
            if duration_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        # Добавление
        new_training = {
            "date": date,
            "type": training_type,
            "duration": duration_val
        }
        self.trainings.append(new_training)
        self.save_data()
        self.refresh_table()
        
        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.type_combo.set("")
        self.duration_entry.delete(0, tk.END)
    
    def refresh_table(self, filtered_list=None):
        """Обновляет таблицу. Если filtered_list не задан, показывает все тренировки."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        data_to_show = filtered_list if filtered_list is not None else self.trainings
        for t in data_to_show:
            self.tree.insert("", tk.END, values=(t["date"], t["type"], t["duration"]))
    
    def apply_filter(self):
        filter_type = self.filter_type_combo.get()
        filter_date = self.filter_date_entry.get().strip()
        
        filtered = self.trainings[:]
        
        if filter_type != "Все":
            filtered = [t for t in filtered if t["type"] == filter_type]
        
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре! Используйте ГГГГ-ММ-ДД")
                return
            filtered = [t for t in filtered if t["date"] == filter_date]
        
        self.refresh_table(filtered)
    
    def reset_filter(self):
        self.filter_type_combo.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.refresh_table()
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.trainings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.trainings = []
        else:
            self.trainings = []
    
    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
