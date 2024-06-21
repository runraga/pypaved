class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)

    def start_processing(self):
        self.model.start_processing(self.view.update_progress)

    def stop_processing(self):
        self.model.stop_processing()

    def get_progress(self):
        return self.model.get_progress()
