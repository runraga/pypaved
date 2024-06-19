import tkinter
import customtkinter as ctk


class RowManager:
    def __init__(self):
        self.current_row = 0

    def get_row_number(self):

        return self.current_row

    def increment_row(self):
        self.current_row += 1


def reduce_timepoint():
    print("reduce timepoint")


def increase_timepoint():
    print("increase timepoint")


rows = RowManager()

# setup system
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# app grame
app = ctk.CTk()
app.geometry("720x480")
app.title("PAVED")

# add components
path_label = ctk.CTkLabel(app, text="Specify cluster file path:")
path_label.grid(column=0, row=rows.get_row_number(), columnspan=3)
rows.increment_row()

title = ctk.CTkLabel(app, text="Select a time point")
title.grid(column=0, row=rows.get_row_number(), columnspan=3)
rows.increment_row()

left = ctk.CTkButton(app, text="<", width=50, height=50, command=reduce_timepoint)

exposure = ctk.CTkLabel(app, text="Exposure")
exposure.grid(column=1, row=rows.get_row_number(), padx=20)

right = ctk.CTkButton(app, text=">", width=50, height=50, command=increase_timepoint)

left.grid(
    column=0, row=rows.get_row_number()
)  # grid dynamically divides the space in a grid
right.grid(column=2, row=rows.get_row_number())
rows.increment_row()


# run app
app.mainloop()
