import tkinter
import customtkinter as ctk


def reduce_timepoint():
    print("reduce timepoint")


def increase_timepoint():
    print("increase timepoint")


# setup system
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# app grame
app = ctk.CTk()
app.geometry("720x480")
app.title("PAVED")

# add components
title = ctk.CTkLabel(app, text="Select a time point")
title.grid(column=1, row=0)

left = ctk.CTkButton(app, text="<", width=50, height=50, command=reduce_timepoint)

exposure = ctk.CTkLabel(app, text="Exposure")
exposure.grid(column=1,row=1)

right = ctk.CTkButton(app, text=">", width=50, height=50, command=increase_timepoint)

left.grid(column=0, row=1)  # grid dynamically divides the space in a grid
right.grid(column=2, row=1)

# run app
app.mainloop()
