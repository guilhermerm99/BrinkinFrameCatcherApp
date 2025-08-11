# utils.py
import os
import sys
import subprocess
from tkinter import messagebox

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def format_time(seconds):
    """ Formata o tempo em segundos para o formato H-M-S, ideal para nomes de arquivo. """
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}-{m:02d}-{s:02d}"

def open_folder_in_explorer(path):
    """Abre uma pasta no explorador de arquivos padrão do sistema operacional."""
    if not os.path.isdir(path):
        messagebox.showwarning("Diretório não encontrado", f"O diretório '{path}' não foi encontrado.")
        return
        
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin": # macOS
            subprocess.Popen(["open", path])
        else: # linux
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Erro ao Abrir Pasta", f"Não foi possível abrir o diretório:\n{e}")