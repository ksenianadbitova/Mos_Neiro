import customtkinter as ctk
from database import get_stats, get_history


class StatsScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text="📊 Твой прогресс",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkButton(self, text="🔄 Обновить", command=self.refresh).pack(pady=5)

        ctk.CTkLabel(self, text="📜 Последние запросы:",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=30, pady=(15, 5))

        self.history = ctk.CTkTextbox(self, font=ctk.CTkFont(size=13), wrap="word")
        self.history.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.refresh()

    def refresh(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        rows = get_stats()
        names = {"math": "🧮 Математика", "physics": "⚛️ Физика", "english": "🗣️ Английский"}
        for i, (subj, solved, correct) in enumerate(rows):
            card = ctk.CTkFrame(self.stats_frame, corner_radius=12)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            self.stats_frame.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(card, text=names.get(subj, subj),
                         font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(10, 2))
            ctk.CTkLabel(card, text=f"Решено: {solved}",
                         font=ctk.CTkFont(size=13)).pack()
            ctk.CTkLabel(card, text=f"Верно: {correct} ✅",
                         font=ctk.CTkFont(size=13)).pack(pady=(0, 10))

        self.history.delete("1.0", "end")
        for subj, q, a, ts in get_history(50):
            self.history.insert("end", f"[{ts}] ({subj})\n❓ {q}\n💬 {a[:200]}\n{'-'*50}\n")