import customtkinter as ctk
from src.view.row_manager import RowManager


class ProgressWindow:
    def __init__(self):
        self.rows = RowManager()
        self.progress_window = ctk.CTkToplevel()
        self.progress_window.title("Data progressing progress")
        self.progress_window.geometry("500x100+0+0")

        self.label_frame = ctk.CTkFrame(self.progress_window)
        self.label_frame.pack(fill="both", expand=True)

        self.progress_processes = {}
        starting_label = self.add_label("Processing cluster data...")

    def add_label(self, text):
        label_text = ctk.StringVar(value=text)
        path_label = ctk.CTkLabel(
            self.label_frame,
            textvariable=label_text,
            anchor="w",
        )
        path_label.pack(
            anchor="w",
            padx=5,
            pady=2,
        )
        self.progress_processes["Processing cluster data..."] = path_label

        self.progress_window.update_idletasks()
        self.progress_window.update()
        frame_height = self.label_frame.winfo_height()
        window_height = self.progress_window.winfo_height()
        height = len(self.progress_processes.keys()) * 50
        self.progress_window.geometry(f"{self.progress_window.winfo_width()}x{height}")

        return label_text

    def progress_update(self, process, progress):

        if process in self.progress_processes:
            self.update_progress_label(process, progress)
        else:
            self.progress_processes[process] = self.add_label(f"{process}: {progress}")

    def update_progress_label(self, process, progress):
        self.progress_processes[process].set(f"{process}: {progress}")

    def close_progress_window(self):
        self.progress_window.destroy()
