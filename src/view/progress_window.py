import customtkinter as ctk
from src.view.row_manager import RowManager


class ProgressWindow:
    def __init__(self):
        self.rows = RowManager()
        self.progress_window = ctk.CTkToplevel()
        self.progress_window.title("Data progressing progress")
        self.progress_window.geometry("300x100x0x0")

        self.label_frame = ctk.CTkFrame(self.progress_window)
        self.label_frame.pack(fill="both", expand=True)

        starting_label = self.add_label("Processing cluster data...")
        self.progress_processes = {"Processing cluster data...": starting_label}

    def add_label(self, text):
        label_text = ctk.StringVar(value=text)
        self.path_label = ctk.CTkLabel(
            self.label_frame,
            textvariable=label_text,
            anchor="w",
        )
        self.path_label.pack(
            anchor="w",
            padx=5,
            pady=2,
        )
        self.progress_window.update_idletasks()
        frame_height = self.label_frame.winfo_height()
        self.progress_window.geometry(
            f"{self.progress_window.winfo_width()}x{frame_height + 50}"
        )

        return label_text

    def progress_update(self, process, progress):
        if process in self.progress_processes:
            self.update_progress_label(process, progress)
        else:
            self.progress_processes[process] = self.add_label(f"{process}: {progress}")

    # def add_new_progress_label(self, process, progress):
    #     self.progress_processes[process].set(value=f"{process}: {progress}")

    def update_progress_label(self, process, progress):
        self.progress_processes[process].set(value=f"{process}: {progress}")

    def close_progress_window(self):
        self.progress_window.destroy()
