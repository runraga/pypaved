from tkinter import Tk, Button, Label

class View:
    def __init__(self, root):
        self.root = root
        self.controller = None

        self.start_button = Button(root, text="Start", command=self.start)
        self.start_button.pack(pady=10)

        self.stop_button = Button(root, text="Stop", command=self.stop)
        self.stop_button.pack(pady=10)

        self.progress_label = Label(root, text="Progress: 0%")
        self.progress_label.pack(pady=10)

    def set_controller(self, controller):
        self.controller = controller

    def start(self):
        if self.controller:
            self.controller.start_processing()

    def stop(self):
        if self.controller:
            self.controller.stop_processing()

    def update_progress(self, progress, total):
        percent = (progress / total) * 100
        self.progress_label.config(text=f"Progress: {percent:.2f}%")
        self.root.update_idletasks()
