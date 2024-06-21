import os
import threading
from src.view.GUI import GUI
from src.model.process_cluster_data import Model


class Controller:
    def __init__(self, app):
        self.view = GUI(app, self)
        self.app = app
        self.model = None
        self.thread = None

    # new model and process data from provided path
    def check_thread(self):
        if self.thread.is_alive():
            self.view.app.after(100, self.check_thread)
        else:
            self.view.close_progress_window()
            self.retrieve_data()

    def retrieve_data(self):
        states, exposures, proteins = self.model.get_states_protein_exposure_lists()
        self.view.new_model(states, exposures, proteins)

        data = self.__get_data_from_model()

        self.view.create_plot_window(data)

    def process_cluster(self, sim_path=""):
        if sim_path:
            path = sim_path
        else:
            path = self.view.path_text.get()
        if os.path.exists(path) & os.path.isfile(path) & path.endswith(".csv"):
            if sim_path:
                self.model = Model(sim_path)
            else:
                self.model = Model(path)
            self.view.new_progress_window()
            self.thread = threading.Thread(
                target=self.model.start_process, args=(self.update_progress,)
            )
            self.thread.start()
            self.check_thread()
            # close progress window

        else:
            self.view.file_path_error()
            self.app.after(100, lambda: self.view.path_text.focus_set())

    def update_progress(self, process, progress):
        # progress will be a string
        self.view.update_progress(process, progress)
        # call progress window with updates

    def __get_data_from_model(self):

        if self.view.reference_checkbox.get():
            dataset = self.model.get_dataset(
                self.view.get_selected_protein(),
                self.view.get_selected_exposure(),
                self.view.get_selected_state(),
            )
            self.view.set_chart_min_max(dataset["min_max"])
            return dataset["data"]
        else:
            dataset = self.model.get_dataset(
                self.view.get_selected_protein(),
                self.view.get_selected_exposure(),
            )
            self.view.set_chart_min_max(dataset["min_max"])

            return dataset["data"]

    def decrease_exposure(self):
        self.view.decrease_exposure()
        data = data = self.__get_data_from_model()
        self.view.update_plot(data)

    def increase_exposure(self):
        self.view.increase_exposure()
        data = self.__get_data_from_model()
        self.view.update_plot(data)

    def change_protein(self, _):
        data = self.__get_data_from_model()
        self.view.update_plot(data)

    def change_ref_state(self, _):
        data = self.__get_data_from_model()
        self.view.update_plot(data)

    def ref_checkbox_change(self):
        data = self.__get_data_from_model()
        self.view.update_plot(data)
        if self.view.reference_checkbox.get():
            self.view.state_dropdown.configure(state="readonly")
        else:
            self.view.state_dropdown.configure(state="disabled")

    def remove_model(self):
        self.model = None
        self.view.model_removed()
