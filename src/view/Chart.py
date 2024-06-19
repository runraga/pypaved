import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.lines as Line2D
from src.model.process_cluster_data import Model
import customtkinter as ctk
import re


class ChartWindow:
    def __init__(self, data, app):
        self.plot_window = ctk.CTkToplevel()
        self.plot_window.title("PAVED plot")
        self.app = app
        self.plot_window.geometry(self.calc_position())
        # self.plot_window.config(width=720, height=480)

        self.data = None
        self.fig, self.ax = plt.subplots()
        self.update_chart(data)

    def calc_position(self):
        main_window_size_position = self.app.app.geometry()
        pattern = r"\d+"
        dims = re.findall(pattern, main_window_size_position)
        dims = list(map(int, dims))

        x = dims[0] + dims[2]
        y = dims[3]

        return f"720x480+{x}+{y}"

    def plot_exposures(self, exposure_group):
        # fig.suptitle(exposure_group.iloc[0]["Exposure"])
        # for index, row in exposure_group.iterrows():
        p_threshold = 0.05
        state = exposure_group.name
        full_positions = pd.Series(
            range(1, exposure_group["Position"].max() + 1), name="Position"
        )

        exposure_group = pd.merge(
            full_positions, exposure_group, on="Position", how="left"
        )
        self.ax.plot(
            exposure_group["Position"],
            exposure_group["Combined Mean"],
            linewidth=2,
            label=state,
        )

        def check_significance(row):
            # try:
            if row["p_value"] < 0.05:
                return row["Combined Mean"] + 0.0025
            # except TypeError:
            else:
                return np.NaN

        if "p_value" in exposure_group:
            exposure_group["is_significant"] = exposure_group.apply(
                check_significance, axis=1
            )
            # print("updated:", exposure_group["is_significant"])
            self.ax.plot(
                exposure_group["Position"],
                exposure_group["is_significant"],
                ".k",
                linewidth=2,
                markersize=1,
            )
        self.ax.fill_between(
            exposure_group["Position"],
            exposure_group["Combined Mean"]
            - np.sqrt(exposure_group["Combined Variance"]),
            exposure_group["Combined Mean"]
            + np.sqrt(exposure_group["Combined Variance"]),
            alpha=0.10,
            linewidth=0.5,
        )

    def remove_plot(self):
        self.plot_window.destroy()

    def update_chart(self, data):
        if plt.gcf().number > 0:
            self.fig.clf()
            self.ax = self.fig.add_subplot(111)
        self.data = data
        self.fig.tight_layout()
        self.data.groupby("State").apply(self.plot_exposures, include_groups=False)
        if "p_value" in data:
            self.ax.scatter(
                [], [], color="black", label="Significant difference", marker="."
            )
        self.ax.legend(loc=3, bbox_to_anchor=(1, 0), fontsize="small")
        self.fig.tight_layout()

        plot_frame = ctk.CTkFrame(self.plot_window)
        plot_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_window)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=0, rely=0, relwidth=1, relheight=0.9)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_window)
        self.toolbar.update()
        self.toolbar.place(relx=0, rely=0.9, relwidth=1, relheight=0.1)
