import tkinter as tk


class BreakWindow(tk.Toplevel):

    def __init__(self, parent, break_minutes, on_finish):
        super().__init__(parent)
        self.seconds = break_minutes * 60
        self.on_finish = on_finish
        self.title("Перерыв")
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.disable_close)
        self.attributes("-topmost", True)
        self.grab_set()
        self.focus_force()

        width = 900
        height = 400

        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.attributes("-toolwindow", True)
        self.attributes("-topmost", True)

        tk.Label(self,text="Сделай перерыв для глаз!",font=("Arial", 18),).pack(pady=20)
        self.timer_label = tk.Label(self,font=("Arial", 24),)

        self.timer_label.pack()

        self.protocol("WM_DELETE_WINDOW", self.disable_close)
        self.update_timer()

    def update_timer(self):
        mins = self.seconds // 60
        secs = self.seconds % 60

        self.timer_label.config(text=f"{mins:02}:{secs:02}")

        if self.seconds > 0:
            self.seconds -= 1
            self.after(1000, self.update_timer)
        else:
            self.force_close()

    def disable_close(self):
        pass

    def force_close(self):
        self.destroy()
        self.on_finish()