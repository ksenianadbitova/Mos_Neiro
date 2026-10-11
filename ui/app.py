import customtkinter as ctk
import theme


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("МосНейро")
        self.geometry("1280x820")
        self.minsize(1024, 640)

        # Тема
        mode = theme.current_mode()
        ctk.set_appearance_mode("light" if mode == "light" else "dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=theme.BG_DARK)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_key = "home"
        self.sidebar = None
        self.content = None
        self.current_frame = None

        from ui.sidebar import Sidebar
        self.sidebar = Sidebar(self, on_select=self.show)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.show("home")

    def show(self, key: str):
        self.current_key = key
        if self.current_frame is not None:
            try:
                self.current_frame.destroy()
            except Exception:
                pass

        try:
            self.sidebar.set_active(key)
        except Exception:
            pass

        # Загрузка экрана
        try:
            if key == "home":
                from ui.home_screen import HomeScreen
                self.current_frame = HomeScreen(self.content, on_navigate=self.show)
            elif key == "math":
                from ui.math_screen import MathScreen
                self.current_frame = MathScreen(self.content)
            elif key == "physics":
                from ui.physics_screen import PhysicsScreen
                self.current_frame = PhysicsScreen(self.content)
            elif key == "chatbot":
                from ui.chatbot_screen import ChatbotScreen
                self.current_frame = ChatbotScreen(self.content)
            elif key == "web":
                from ui.web_screen import WebScreen
                self.current_frame = WebScreen(self.content)
            elif key == "documents":
                from ui.documents_screen import DocumentsScreen
                self.current_frame = DocumentsScreen(self.content)
            elif key == "library":
                from ui.library_screen import LibraryScreen
                self.current_frame = LibraryScreen(self.content)
            elif key == "gost":
                from ui.gost_screen import GostScreen
                self.current_frame = GostScreen(self.content)
            elif key == "settings":
                from ui.settings_screen import SettingsScreen
                self.current_frame = SettingsScreen(self.content)
        except Exception as e:
            # Заглушка при ошибке
            self.current_frame = ctk.CTkFrame(self.content, fg_color="transparent")
            ctk.CTkLabel(self.current_frame,
                         text=f"⚠️ Не удалось загрузить раздел «{key}»\n\n{e}",
                         font=(theme.FONT_FAMILY, 13),
                         text_color=theme.ERROR,
                         justify="center").pack(expand=True)

        if self.current_frame is not None:
            self.current_frame.grid(row=0, column=0, sticky="nsew")
