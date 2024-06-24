import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from src.view.Chart import ChartWindow
from src.view.row_manager import RowManager
from src.view.progress_window import ProgressWindow


class GUI:
    def __init__(self, app, controller):
        self.states = ["No data"]
        self.exposures = ["No data"]
        self.proteins = ["No data"]
        self.progress_window = None
        self.chart = None

        self.app = app
        self.controller = controller
        self.rows = RowManager()

        self.path_label = ctk.CTkLabel(app, text="Specify cluster file path:")
        self.path_label.grid(column=0, row=self.rows.get_row_number(), columnspan=3)
        self.rows.increment_row()

        self.path_text = ctk.CTkEntry(app, placeholder_text="Enter cluster file path")
        self.path_text.grid(column=0, row=self.rows.get_row_number(), columnspan=3)
        self.rows.increment_row()

        self.process_button = ctk.CTkButton(
            app,
            text="Process",
            width=50,
            height=20,
            command=self.controller.process_cluster,
        )
        self.process_button.grid(
            column=1,
            row=self.rows.get_row_number(),
            pady=(2, 20),
        )
        self.rows.increment_row()

        self.title = ctk.CTkLabel(app, text="Select a time point")
        self.title.grid(column=0, row=self.rows.get_row_number(), columnspan=3)
        self.rows.increment_row()

        self.left = ctk.CTkButton(
            app,
            text="-",
            width=30,
            height=25,
            command=self.controller.decrease_exposure,
            state="disabled",
        )

        self.exposure_label = ctk.CTkLabel(app, text=self.states[0])
        self.exposure_label.grid(
            column=1,
            row=self.rows.get_row_number(),
            padx=20,
        )

        self.right = ctk.CTkButton(
            app,
            text="+",
            width=30,
            height=25,
            command=self.controller.increase_exposure,
            state="disabled",
        )

        self.left.grid(
            column=0,
            row=self.rows.get_row_number(),
            padx=20,
        )
        self.right.grid(
            column=2,
            row=self.rows.get_row_number(),
            padx=20,
        )
        self.rows.increment_row()

        self.choose_protein_label = ctk.CTkLabel(app, text="Choose a seqeunce:")
        self.choose_protein_label.grid(
            column=0,
            row=self.rows.get_row_number(),
            columnspan=3,
            pady=(15, 2),
        )
        self.rows.increment_row()

        self.protein_dropdown_var = ctk.StringVar(value="{no data}")

        self.protein_dropdown = ctk.CTkComboBox(
            master=app,
            values=["{no data}"],
            command=controller.change_protein,
            state="disabled",
            variable=self.protein_dropdown_var,
        )
        self.protein_dropdown.grid(
            padx=20, pady=5, row=self.rows.get_row_number(), columnspan=3
        )
        self.rows.increment_row()
        self.check_var = ctk.IntVar(value=1)

        self.reference_checkbox = ctk.CTkCheckBox(
            app,
            text="Show uptake relative to reference:",
            command=self.controller.ref_checkbox_change,
            onvalue=1,
            offvalue=0,
            state="disabled",
            variable=self.check_var,
        )

        self.reference_checkbox.grid(
            padx=20,
            pady=(20, 2),
            column=0,
            row=self.rows.get_row_number(),
            columnspan=3,
        )
        self.rows.increment_row()

        self.state_dropdown_var = ctk.StringVar(value="{no data}")

        self.state_dropdown = ctk.CTkComboBox(
            master=app,
            values=["{no data}"],
            command=controller.change_ref_state,
            state="disabled",
            variable=self.state_dropdown_var,
        )
        self.state_dropdown.grid(
            padx=20, pady=5, row=self.rows.get_row_number(), columnspan=3
        )
        self.rows.increment_row()

        self.reset_button = ctk.CTkButton(
            app,
            text="Reset",
            width=50,
            height=20,
            command=self.controller.remove_model,
            state="disabled",
        )
        self.reset_button.grid(
            column=1,
            row=self.rows.get_row_number(),
            pady=(20, 20),
        )
        self.rows.increment_row()

    def set_states(self, states_list, disable=False):
        state = "disabled" if disable else "readonly"
        self.states = states_list
        self.state_dropdown.configure(values=states_list)
        self.state_dropdown.configure(state=state)
        self.state_dropdown_var.set(self.states[0])

    def set_exposures(self, exposures_list, disable=False):
        if 0 in exposures_list:
            exposures_list.remove(0)
        exposures_list.sort()
        state = "disabled" if disable else "normal"
        self.exposures = exposures_list
        self.exposure_label.configure(text=self.exposures[0])
        self.right.configure(state=state)
        if disable:
            self.left.configure(state=state)
            self.app.update()

    def set_proteins(self, protein_list, disable=False):
        state = "disabled" if disable else "readonly"
        self.proteins = protein_list
        self.protein_dropdown.configure(values=self.proteins)
        self.protein_dropdown.configure(state=state)
        self.protein_dropdown_var.set(self.proteins[0])

    def new_model(self, states, exposures, proteins):
        self.set_states(states)
        self.set_exposures(exposures)
        self.set_proteins(proteins)
        self.reference_checkbox.configure(state="normal")
        self.reset_button.configure(state="normal")
        self.process_button.configure(state="disabled")
        self.path_text.configure(state="disabled")

    def create_plot_window(self, data):
        self.chart = ChartWindow(data, self)

    def model_removed(self):
        self.set_states(["No data"], disable=True)
        self.set_exposures(["No data"], disable=True)
        self.set_proteins(["No data"], disable=True)
        self.reference_checkbox.configure(state="disabled")
        self.reset_button.configure(state="disabled")
        self.path_text.delete(0, ctk.END)
        self.chart.remove_plot()
        self.chart = None
        self.process_button.configure(state="normal")
        self.path_text.configure(state="normal")

    def increase_exposure(self):
        current_exp = self.exposure_label.cget("text")
        new_index = self.exposures.index(current_exp) + 1
        if new_index + 1 == len(self.exposures):
            self.right.configure(state="disabled")
        if new_index == 1:
            self.left.configure(state="normal")
        new_exposure = self.exposures[new_index]
        self.exposure_label.configure(text=new_exposure)

    def decrease_exposure(self):
        current_exp = self.exposure_label.cget("text")
        new_index = self.exposures.index(current_exp) - 1
        if new_index == 0:
            self.left.configure(state="disabled")
        if new_index == len(self.exposures) - 2:
            self.right.configure(state="normal")
        new_exposure = self.exposures[new_index]
        self.exposure_label.configure(text=new_exposure)

    def get_selected_protein(self):
        return self.protein_dropdown_var.get()

    def get_selected_exposure(self):
        return self.exposure_label.cget("text")

    def get_selected_state(self):
        return self.state_dropdown_var.get()

    def update_plot(self, data):
        self.chart.update_chart(data)

    def file_path_error(self):
        CTkMessagebox(
            title="Error",
            message="Invalid path. Check file exists and is a csv file.",
            icon="cancel",
        )

    def new_progress_window(self):
        self.progress_window = ProgressWindow()

    def update_progress(self, process, progress):
        self.progress_window.progress_update(process, progress)

    def close_progress_window(self):
        self.progress_window.close_progress_window()
        self.progress_window = None

    def set_chart_min_max(self, min_max):
        if self.chart != None:
            self.chart.set_min_max(min_max)
