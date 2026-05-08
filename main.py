import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

# Файл для сохранения истории
HISTORY_FILE = "quotes_history.json"

# Предопределенный список цитат (Текст, Автор, Тема)
QUOTES_DB = [
    {"text": "Единственный способ сделать выдающуюся работу — искренне любить то, что делаешь.", "author": "Стив Джобс", "topic": "Работа"},
    {"text": "Успех — это способность идти от поражения к поражению, не теряя энтузиазма.", "author": "Уинстон Черчилль", "topic": "Успех"},
    {"text": "Жизнь — это то, что случается с вами, пока вы строите другие планы.", "author": "Джон Леннон", "topic": "Жизнь"},
    {"text": "Логика приведет вас из пункта А в пункт Б. Воображение приведет вас куда угодно.", "author": "Альберт Эйнштейн", "topic": "Творчество"},
    {"text": "Не бойтесь отказаться от хорошего, чтобы перейти к великому.", "author": "Джон Д. Рокфеллер", "topic": "Успех"},
    {"text": "Счастье — это не что-то готовое. Оно происходит от ваших собственных действий.", "author": "Далай-лама", "topic": "Счастье"},
    {"text": "Лучшая месть — огромный успех.", "author": "Фрэнк Синатра", "topic": "Жизнь"},
    {"text": "Время — это самый ценный ресурс, который у нас есть.", "author": "Тим Феррис", "topic": "Время"},
    {"text": "Мы — то, что мы постоянно делаем. Совершенство — это не действие, а привычка.", "author": "Аристотель", "topic": "Развитие"},
    {"text": "Никогда не поздно стать тем, кем тебе хочется быть.", "author": "Джордж Элиот", "topic": "Жизнь"}
]

class QuoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("600x500")
        
        self.history = []
        self.load_history()
        
        # Переменные для фильтров
        self.author_filter = tk.StringVar()
        self.topic_filter = tk.StringVar()
        
        self.create_widgets()
        self.update_filters()
        
    def create_widgets(self):
        # --- Верхняя панель: Отображение цитаты ---
        display_frame = tk.LabelFrame(self.root, text="Текущая цитата", padx=10, pady=10)
        display_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.quote_label = tk.Label(display_frame, text="Нажмите кнопку, чтобы получить цитату", 
                                    wraplength=500, justify="center", font=("Arial", 12, "italic"))
        self.quote_label.pack(pady=10)
        
        self.author_label = tk.Label(display_frame, text="", font=("Arial", 10, "bold"))
        self.author_label.pack()
        
        # Кнопка генерации
        self.generate_btn = tk.Button(self.root, text="Сгенерировать цитату", command=self.generate_quote, 
                                      bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.generate_btn.pack(pady=10)
        
        # --- Панель управления: Фильтры и Добавление ---
        control_frame = tk.LabelFrame(self.root, text="Управление", padx=10, pady=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтры
        filter_frame = tk.Frame(control_frame)
        filter_frame.pack(fill="x", pady=5)
        
        tk.Label(filter_frame, text="Фильтр по автору:").grid(row=0, column=0, sticky="w")
        self.author_combo = ttk.Combobox(filter_frame, textvariable=self.author_filter, state="readonly")
        self.author_combo.grid(row=0, column=1, padx=5)
        self.author_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        tk.Label(filter_frame, text="Фильтр по теме:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.topic_combo = ttk.Combobox(filter_frame, textvariable=self.topic_filter, state="readonly")
        self.topic_combo.grid(row=0, column=3, padx=5)
        self.topic_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Кнопка сброса фильтров
        reset_btn = tk.Button(control_frame, text="Сбросить фильтры", command=self.reset_filters)
        reset_btn.pack(pady=5)
        
        # Форма добавления новой цитаты
        add_frame = tk.Frame(control_frame)
        add_frame.pack(fill="x", pady=10)
        
        tk.Label(add_frame, text="Новая цитата:").grid(row=0, column=0, sticky="w")
        self.new_text = tk.Entry(add_frame, width=30)
        self.new_text.grid(row=0, column=1, padx=5)
        
        tk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_author = tk.Entry(add_frame, width=30)
        self.new_author.grid(row=1, column=1, padx=5)
        
        tk.Label(add_frame, text="Тема:").grid(row=2, column=0, sticky="w", pady=5)
        self.new_topic = tk.Entry(add_frame, width=30)
        self.new_topic.grid(row=2, column=1, padx=5)
        
        add_btn = tk.Button(control_frame, text="Добавить цитату в базу", command=self.add_quote)
        add_btn.pack(pady=5)
        
        # --- История ---
        history_frame = tk.LabelFrame(self.root, text="История генерации", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Список для истории
        self.history_listbox = tk.Listbox(history_frame, height=8)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(history_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        
        self.refresh_history_list()

    def generate_quote(self):
        # Фильтрация базы перед выбором
        filtered_quotes = self.get_filtered_quotes()
        
        if not filtered_quotes:
            messagebox.showwarning("Нет данных", "Нет цитат, соответствующих выбранным фильтрам.")
            return

        quote = random.choice(filtered_quotes)
        
        # Отображение
        self.quote_label.config(text=f'"{quote["text"]}"')
        self.author_label.config(text=f"- {quote['author']} ({quote['topic']})")
        
        # Сохранение в историю
        history_entry = f"{quote['text']} | {quote['author']} | {quote['topic']}"
        self.history.append(history_entry)
        
        # Сохранение в JSON
        self.save_history()
        self.refresh_history_list()

    def get_filtered_quotes(self):
        author = self.author_filter.get()
        topic = self.topic_filter.get()
        
        result = QUOTES_DB
        
        if author:
            result = [q for q in result if q['author'] == author]
        if topic:
            result = [q for q in result if q['topic'] == topic]
            
        return result

    def update_filters(self):
        # Обновление выпадающих списков
        authors = sorted(list(set(q['author'] for q in QUOTES_DB)))
        topics = sorted(list(set(q['topic'] for q in QUOTES_DB)))
        
        self.author_combo['values'] = authors
        self.topic_combo['values'] = topics
        self.author_combo.set('')
        self.topic_combo.set('')

    def apply_filters(self, event=None):
        # Просто обновляем список, если нужно, но логика фильтрации уже в generate_quote
        # Можно добавить визуальное обновление базы, если нужно
        pass

    def reset_filters(self):
        self.author_filter.set('')
        self.topic_filter.set('')

    def add_quote(self):
        text = self.new_text.get().strip()
        author = self.new_author.get().strip()
        topic = self.new_topic.get().strip()
        
        # Валидация
        if not text or not author or not topic:
            messagebox.showerror("Ошибка ввода", "Все поля (Цитата, Автор, Тема) должны быть заполнены!")
            return
        
        new_quote = {"text": text, "author": author, "topic": topic}
        QUOTES_DB.append(new_quote)
        self.update_filters() # Обновить списки фильтров
        
        # Очистка полей
        self.new_text.delete(0, tk.END)
        self.new_author.delete(0, tk.END)
        self.new_topic.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Цитата успешно добавлена в базу!")

    def refresh_history_list(self):
        self.history_listbox.delete(0, tk.END)
        for entry in self.history:
            self.history_listbox.insert(tk.END, entry)

    def save_history(self):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []
        else:
            self.history = []

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteApp(root)
    root.mainloop()
