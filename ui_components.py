# ui_components.py
import customtkinter as ctk
from PIL import Image, ImageTk

class LoadingAnimation:
    """Gerencia a exibição e animação de um GIF de carregamento."""
    def __init__(self, master, gif_path):
        self.master = master
        self.label = ctk.CTkLabel(self.master, text="", bg_color="transparent")
        
        self.frames = []
        try:
            gif_image = Image.open(gif_path)
            for i in range(gif_image.n_frames):
                gif_image.seek(i)
                frame_resized = gif_image.copy().resize((40, 40), Image.Resampling.LANCZOS) 
                self.frames.append(ImageTk.PhotoImage(frame_resized))
            self.delay = gif_image.info.get('duration', 100)
        except FileNotFoundError:
            print(f"Arquivo de animação não encontrado em: {gif_path}")
            self.frames = None
            self.delay = 100

        self.frame_index = 0
        self.animation_task = None

    def place(self, **kwargs):
        if self.frames:
            self.label.place(**kwargs)

    def pack(self, **kwargs):
        if self.frames:
            self.label.pack(**kwargs)
            
    def pack_forget(self):
        self.label.pack_forget()

    def _animate(self):
        if not self.frames: return
        self.label.configure(image=self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.animation_task = self.master.after(self.delay, self._animate)

    def start(self):
        if not self.frames: return
        self.label.lift()
        self.label.configure(image=self.frames[0])
        self._animate()

    def stop(self):
        if self.animation_task:
            self.master.after_cancel(self.animation_task)
            self.animation_task = None
        self.label.configure(image=None)