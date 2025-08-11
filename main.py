# main.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os

# Importações dos nossos módulos locais
from utils import resource_path, format_time, open_folder_in_explorer
from ui_components import LoadingAnimation
from video_processor import extract_frames

# --- Constantes de Configuração ---
class AppConfig:
    DEFAULT_INTERVAL = 1
    WINDOW_TITLE = "Brinkin Frame Catcher"
    ICON_PATH = "assets/icone.ico"
    LOADING_GIF_PATH = "assets/loading.gif"

class AppColors:
    SUCCESS = "#2ECC71"
    ERROR = "#E74C3C"
    WARNING = "#F39C12"
    DEFAULT = ctk.ThemeManager.theme["CTkLabel"]["text_color"]

class FrameCatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(AppConfig.WINDOW_TITLE)
        self.iconbitmap(resource_path(AppConfig.ICON_PATH))
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.video_path = ""
        self.output_dir = ""
        self.specific_times = []
        self.stop_event = threading.Event()
        self._build_ui()
        self.switch_mode()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) 
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.file_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.file_frame, text="1. Selecione o Vídeo e o Destino", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=5)
        self.video_button = ctk.CTkButton(self.file_frame, text="Selecionar Vídeo...", command=self.select_video)
        self.video_button.grid(row=1, column=0, padx=10, pady=5)
        self.video_path_label = ctk.CTkLabel(self.file_frame, text="Nenhum vídeo selecionado", anchor="w")
        self.video_path_label.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.output_button = ctk.CTkButton(self.file_frame, text="Salvar em...", command=self.select_output_dir)
        self.output_button.grid(row=2, column=0, padx=10, pady=5)
        self.output_dir_label = ctk.CTkLabel(self.file_frame, text="Nenhuma pasta selecionada", anchor="w")
        self.output_dir_label.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        self.video_duration_label = ctk.CTkLabel(self.file_frame, text="", text_color="gray")
        self.video_duration_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        self.thumbnail_label = ctk.CTkLabel(self, text="")
        self.thumbnail_label.grid(row=1, column=0, padx=10, pady=5)
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(self.options_frame, text="2. Escolha o Modo de Extração", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
        self.mode_var = ctk.StringVar(value="Especifico")
        self.radio_especifico = ctk.CTkRadioButton(self.options_frame, text="Tempos Específicos", variable=self.mode_var, value="Especifico", command=self.switch_mode)
        self.radio_especifico.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.radio_intervalo = ctk.CTkRadioButton(self.options_frame, text="Intervalo Fixo", variable=self.mode_var, value="Intervalo", command=self.switch_mode)
        self.radio_intervalo.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        self.interval_panel = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.interval_panel.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.interval_panel, text="Extrair 1 frame a cada:").grid(row=0, column=0, padx=5, sticky="w")
        interval_frame = ctk.CTkFrame(self.interval_panel, fg_color="transparent")
        interval_frame.grid(row=0, column=1, sticky="w")
        self.interval_spinbox = ctk.CTkEntry(interval_frame, width=50)
        self.interval_spinbox.pack(side="left")
        self.interval_spinbox.insert(0, str(AppConfig.DEFAULT_INTERVAL))
        ctk.CTkLabel(interval_frame, text="segundo(s)").pack(side="left", padx=5)
        ctk.CTkLabel(self.interval_panel, text="Início (opcional):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        start_time_frame = ctk.CTkFrame(self.interval_panel, fg_color="transparent")
        start_time_frame.grid(row=1, column=1, sticky="w")
        self.start_hour_entry = ctk.CTkEntry(start_time_frame, width=50, placeholder_text="H")
        self.start_hour_entry.pack(side="left", padx=(0,5))
        self.start_min_entry = ctk.CTkEntry(start_time_frame, width=50, placeholder_text="Min")
        self.start_min_entry.pack(side="left", padx=5)
        self.start_sec_entry = ctk.CTkEntry(start_time_frame, width=50, placeholder_text="Seg")
        self.start_sec_entry.pack(side="left", padx=5)
        ctk.CTkLabel(self.interval_panel, text="Fim (opcional):").grid(row=2, column=0, padx=5, sticky="w")
        end_time_frame = ctk.CTkFrame(self.interval_panel, fg_color="transparent")
        end_time_frame.grid(row=2, column=1, sticky="w")
        self.end_hour_entry = ctk.CTkEntry(end_time_frame, width=50, placeholder_text="H")
        self.end_hour_entry.pack(side="left", padx=(0,5))
        self.end_min_entry = ctk.CTkEntry(end_time_frame, width=50, placeholder_text="Min")
        self.end_min_entry.pack(side="left", padx=5)
        self.end_sec_entry = ctk.CTkEntry(end_time_frame, width=50, placeholder_text="Seg")
        self.end_sec_entry.pack(side="left", padx=5)
        self.specific_panel = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.specific_panel.grid_columnconfigure(0, weight=1)
        self.specific_panel.grid_rowconfigure(1, weight=1)
        self.add_time_subframe = ctk.CTkFrame(self.specific_panel, fg_color="transparent")
        self.add_time_subframe.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(self.add_time_subframe, text="Adicionar tempo (H:M:S):").grid(row=0, column=0, columnspan=4, pady=5, sticky="w")
        self.hour_entry = ctk.CTkEntry(self.add_time_subframe, width=50, placeholder_text="Hora")
        self.hour_entry.grid(row=1, column=0, padx=(0,5))
        self.min_entry = ctk.CTkEntry(self.add_time_subframe, width=50, placeholder_text="Min")
        self.min_entry.grid(row=1, column=1, padx=5)
        self.sec_entry = ctk.CTkEntry(self.add_time_subframe, width=50, placeholder_text="Seg")
        self.sec_entry.grid(row=1, column=2, padx=5)
        self.add_time_button = ctk.CTkButton(self.add_time_subframe, text="Adicionar", width=80, command=self.add_specific_time)
        self.add_time_button.grid(row=1, column=3, padx=5)
        self.times_list_frame = ctk.CTkScrollableFrame(self.specific_panel, label_text="Tempos adicionados")
        self.times_list_frame.grid(row=1, column=0, pady=10, sticky="nsew", padx=5)
        self.times_list_frame.grid_columnconfigure(0, weight=1)
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.process_button = ctk.CTkButton(self.action_frame, text="Iniciar Extração", font=ctk.CTkFont(size=14, weight="bold"), command=self.start_extraction_thread, state="disabled")
        self.process_button.pack(pady=10, fill="x", padx=10)
        self.progress_bar = ctk.CTkProgressBar(self.action_frame)
        self.progress_bar.pack(pady=(5,0), fill="x", padx=10)
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(self.action_frame, text="Pronto para iniciar. Selecione um vídeo e uma pasta de destino.")
        self.status_label.pack(pady=(0,5))
        self.loading_animation = LoadingAnimation(self.action_frame, resource_path(AppConfig.LOADING_GIF_PATH))
        self.post_action_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.post_action_frame.grid_columnconfigure((0, 1), weight=1)
        self.open_folder_button = ctk.CTkButton(self.post_action_frame, text="📂 Abrir Pasta de Destino", command=self.open_output_folder)
        self.open_folder_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.reset_button = ctk.CTkButton(self.post_action_frame, text="🔄 Refazer Processo", command=self.reset_application, fg_color="#565B5E", hover_color="#6F7477")
        self.reset_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _parse_time_from_entries(self, h_entry, m_entry, s_entry):
        h_str, m_str, s_str = h_entry.get(), m_entry.get(), s_entry.get()
        if not h_str and not m_str and not s_str:
            return None
        h = h_str or "0"
        m = m_str or "0"
        s = s_str or "0"
        if not all(c.isdigit() for c in [h,m,s]):
            raise ValueError("O tempo deve conter apenas números.")
        return (int(h) * 3600) + (int(m) * 60) + int(s)

    def switch_mode(self):
        if self.mode_var.get() == "Intervalo":
            self.interval_panel.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="w")
            self.specific_panel.grid_forget()
        else:
            self.interval_panel.grid_forget()
            self.specific_panel.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    def add_specific_time(self):
        hour_str = self.hour_entry.get() or "0"
        min_str = self.min_entry.get() or "0"
        sec_str = self.sec_entry.get() or "0"
        if not all(s.isdigit() for s in [hour_str, min_str, sec_str]):
            messagebox.showerror("Erro de Formato", "Por favor, insira apenas números nos campos de tempo.")
            return
        hour, minute, second = int(hour_str), int(min_str), int(sec_str)
        if not (0 <= minute < 60) or not (0 <= second < 60):
            messagebox.showerror("Valor Inválido", "Minutos e segundos devem estar entre 0 e 59.")
            return
        total_seconds = (hour * 3600) + (minute * 60) + second
        if total_seconds not in self.specific_times:
            self.specific_times.append(total_seconds)
            self.specific_times.sort()
            self.redraw_timestamp_list()
        self.hour_entry.delete(0, "end")
        self.min_entry.delete(0, "end")
        self.sec_entry.delete(0, "end")

    def remove_specific_time(self, time_to_remove):
        self.specific_times.remove(time_to_remove)
        self.redraw_timestamp_list()

    def redraw_timestamp_list(self):
        for widget in self.times_list_frame.winfo_children():
            widget.destroy()
        for i, total_seconds in enumerate(self.specific_times):
            time_str = format_time(total_seconds).replace('-', ':')
            item_frame = ctk.CTkFrame(self.times_list_frame)
            item_frame.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            item_frame.grid_columnconfigure(0, weight=1)
            label = ctk.CTkLabel(item_frame, text=time_str)
            label.grid(row=0, column=0, padx=5, sticky="w")
            remove_button = ctk.CTkButton(item_frame, text="X", width=25, height=25, fg_color="transparent", border_color="#565B5E", border_width=1, hover_color="#C85050", command=lambda ts=total_seconds: self.remove_specific_time(ts))
            remove_button.grid(row=0, column=1, padx=5)

    def select_video(self):
        path = filedialog.askopenfilename(filetypes=[("Arquivos de Vídeo", "*.mp4 *.avi *.mov *.mkv")])
        if path:
            self.video_path = path
            self.video_path_label.configure(text=os.path.basename(path))

            try:
                import cv2
                cap = cv2.VideoCapture(self.video_path)
                if not cap.isOpened():
                    raise ValueError("Não foi possível abrir o vídeo")
                
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

                if fps > 0:
                    duration_s = frame_count / fps
                    duration_formatted = format_time(duration_s).replace('-', ':')
                    self.video_duration_label.configure(text=f"Duração do Vídeo: {duration_formatted}")
                else:
                    self.video_duration_label.configure(text="Duração indisponível (FPS=0)")
                
                cap.release()

            except Exception as e:
                print(f"Erro ao obter duração do vídeo: {e}")
                self.video_duration_label.configure(text="Duração indisponível")

            self.update_start_button_state()
            self.show_thumbnail()

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir = path
            self.output_dir_label.configure(text=path)
            self.update_start_button_state()
    
    def show_thumbnail(self):
        try:
            import cv2
            from PIL import Image, ImageTk
            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail((320, 180))
                photo = ImageTk.PhotoImage(image=img)
                self.thumbnail_label.configure(image=photo)
                self.thumbnail_label.image = photo
        except Exception:
            self.thumbnail_label.configure(text="Não foi possível gerar miniatura.")
            self.thumbnail_label.image = None

    def update_start_button_state(self):
        if self.video_path and self.output_dir:
            self.process_button.configure(state="normal")
        else:
            self.process_button.configure(state="disabled")

    def set_ui_state(self, is_enabled):
        state = "normal" if is_enabled else "disabled"
        self.video_button.configure(state=state)
        self.output_button.configure(state=state)
        self.radio_intervalo.configure(state=state)
        self.radio_especifico.configure(state=state)
        self.add_time_button.configure(state=state)
        self.interval_spinbox.configure(state=state)
        for item_frame in self.times_list_frame.winfo_children():
            for widget in item_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(state=state)
    
    def open_output_folder(self):
        if self.output_dir:
            open_folder_in_explorer(self.output_dir)

    def reset_application(self):
        self.video_path = ""
        self.output_dir = ""
        self.specific_times.clear()
        self.video_path_label.configure(text="Nenhum vídeo selecionado")
        self.output_dir_label.configure(text="Nenhuma pasta selecionada")
        self.thumbnail_label.configure(image=None)
        self.thumbnail_label.image = None
        self.video_duration_label.configure(text="")
        self.progress_bar.set(0)
        self.update_status("Pronto para iniciar. Selecione um vídeo e uma pasta de destino.")
        self.redraw_timestamp_list()
        self.post_action_frame.pack_forget()
        self.update_start_button_state()
        self.set_ui_state(True)
        self.process_button.configure(text="Iniciar Extração", command=self.start_extraction_thread, state="disabled", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def update_status(self, text, color=AppColors.DEFAULT):
        self.status_label.configure(text=text, text_color=color)

    def stop_extraction(self):
        self.update_status("Parando processo...", color=AppColors.WARNING)
        self.stop_event.set()
        self.process_button.configure(state="disabled", text="Parando...")

    def start_extraction_thread(self):
        self.set_ui_state(False)
        self.progress_bar.set(0)
        self.post_action_frame.pack_forget()
        self.stop_event.clear()
        self.process_button.configure(text="Parar Extração", command=self.stop_extraction, fg_color="#C0392B", hover_color="#E74C3C", state="normal")
        self.update_status("Preparando para extração...")
        self.loading_animation.pack(pady=10) 
        self.loading_animation.start()
        extraction_thread = threading.Thread(target=self.run_extraction_logic, daemon=True)
        extraction_thread.start()

    def run_extraction_logic(self):
        mode = self.mode_var.get()
        options = {}
        try:
            if mode == "Intervalo":
                options['interval'] = int(self.interval_spinbox.get())
                start_time = self._parse_time_from_entries(self.start_hour_entry, self.start_min_entry, self.start_sec_entry)
                end_time = self._parse_time_from_entries(self.end_hour_entry, self.end_min_entry, self.end_sec_entry)
                if start_time is not None:
                    options['start_time_s'] = start_time
                if end_time is not None:
                    options['end_time_s'] = end_time
            else:
                options['times'] = self.specific_times
        except ValueError as e:
            self.after(0, self.process_extraction_result, {"status": "error", "message": str(e)})
            return

        def progress_callback(progress, message):
            self.after(0, self.update_progress_from_thread, progress, message)

        result = extract_frames(
            self.video_path,
            self.output_dir,
            mode,
            options,
            progress_callback,
            self.stop_event
        )
        self.after(0, self.process_extraction_result, result)

    def update_progress_from_thread(self, progress, message):
        self.progress_bar.set(progress)
        self.update_status(message)

    def process_extraction_result(self, result):
        self.loading_animation.stop()
        self.loading_animation.pack_forget()
        self.set_ui_state(True)
        self.process_button.configure(text="Iniciar Extração", command=self.start_extraction_thread, fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.update_start_button_state()
        status = result.get("status")
        if status == "success":
            final_msg = f"Concluído! {result['frames_saved']} frames salvos com sucesso."
            self.update_status(final_msg, AppColors.SUCCESS)
            messagebox.showinfo("Sucesso", final_msg)
            self.post_action_frame.pack(pady=5, fill="x", padx=10)
            self.open_folder_button.configure(state="normal")
        elif status == "stopped":
            final_msg = f"Processo parado pelo usuário. {result['frames_saved']} frames foram salvos."
            self.update_status(final_msg, AppColors.WARNING)
            messagebox.showwarning("Processo Parado", final_msg)
            self.post_action_frame.pack(pady=5, fill="x", padx=10)
            if result['frames_saved'] > 0:
                self.open_folder_button.configure(state="normal")
            else:
                self.open_folder_button.configure(state="disabled")
        else: # status == "error"
            error_message = result.get("message", "Ocorreu um erro desconhecido.")
            self.update_status(f"Falha: {error_message}", AppColors.ERROR)
            messagebox.showerror("Erro na Extração", error_message)
            self.post_action_frame.pack(pady=5, fill="x", padx=10)
            self.open_folder_button.configure(state="disabled")

if __name__ == "__main__":
    app = FrameCatcherApp()
    app.mainloop()