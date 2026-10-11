import customtkinter as ctk
import config
import theme


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=50, pady=(30, 10))
        ctk.CTkLabel(header, text="⚙️ Настройки",
                     font=(theme.FONT_FAMILY, 28, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Статус окружения и информация о программе",
                     font=(theme.FONT_FAMILY, 13),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=50, pady=(12, 6))

        ctk.CTkButton(
            btn_row, text="🔄 Обновить", width=140, height=34,
            font=(theme.FONT_FAMILY, 12),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF", corner_radius=16,
            command=self.refresh,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row, text="📂 Открыть папку проекта", width=200, height=34,
            font=(theme.FONT_FAMILY, 12),
            fg_color=theme.BG_CARD, hover_color=theme.ACCENT_LIGHT,
            text_color=theme.TEXT_SECONDARY, corner_radius=16,
            border_width=1, border_color=theme.BORDER,
            command=self.open_folder,
        ).pack(side="left", padx=4)

        # Настройки перевода
        settings_box = ctk.CTkFrame(self, fg_color=theme.BG_CARD,
                                    corner_radius=12, border_width=1,
                                    border_color=theme.BORDER)
        settings_box.pack(fill="x", padx=50, pady=(12, 6))
        
        ctk.CTkLabel(settings_box, text="🌐 Настройки перевода",
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 6))
        
        # Проверка Argos
        try:
            import argostranslate.translate as _tr
            argos_ok = True
        except ImportError:
            argos_ok = False
        
        status = "✅ Argos Translate установлен (перевод работает офлайн)" if argos_ok else "⭕ Argos Translate не установлен (перевод только онлайн)"
        ctk.CTkLabel(settings_box, text=status,
                     font=(theme.FONT_FAMILY, 12),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(0, 12))
        
        self.output = ctk.CTkTextbox(
            self, font=(theme.FONT_FAMILY, 13),
            fg_color=theme.BG_CARD, text_color=theme.TEXT_PRIMARY,
            corner_radius=12, wrap="word", border_width=1,
            border_color=theme.BORDER,
        )
        self.output.pack(fill="both", expand=True, padx=50, pady=(10, 30))

        self.refresh()

    def refresh(self):
        try:
            status = config.get_status()
        except Exception as e:
            status = f"❌ Ошибка проверки: {e}"
        self.output.delete("1.0", "end")
        self.output.insert("end", status)

    def open_folder(self):
        import os
        import subprocess
        try:
            path = str(config.PROJECT_ROOT)
            subprocess.Popen(f'explorer "{path}"')
        except Exception:
            pass
