import pandas as pd
import numpy as np
from multiprocessing import Pool
import tkinter as tk
from tkinter import ttk
import threading

# Sample DataFrame creation (for demonstration)
np.random.seed(0)
data = {
    'start': np.random.randint(0, 131, 700),
    'end': np.random.randint(20, 151, 700),
    'mean': np.random.rand(700) * 10,
    'std': np.random.rand(700) * 2,
    'count': np.random.randint(1, 100, 700)
}
df = pd.DataFrame(data)

# Model: Handles the data and logic
class DataModel:
    def __init__(self):
        self.df = df

    def calculate_combined_stats(self, i):
        filtered_df = self.df[(self.df['start'] <= i) & (self.df['end'] >= i)]
        
        if filtered_df.empty:
            return i, np.nan, np.nan
        
        total_count = filtered_df['count'].sum()
        weighted_mean = (filtered_df['mean'] * filtered_df['count']).sum() / total_count
        
        if total_count == 0:
            return i, weighted_mean, np.nan
        
        variance = ((filtered_df['std']**2 * (filtered_df['count'] - 1)).sum() + \
                   filtered_df['count'] * (filtered_df['mean'] - weighted_mean)**2).sum() / (total_count - 1)
        combined_std = np.sqrt(variance)
        
        return i, weighted_mean, combined_std

    def process_range(self, i):
        return self.calculate_combined_stats(i)

    def run_multiprocessing(self, callback):
        range_values = range(1, 151)
        with Pool() as pool:
            results = pool.map(self.process_range, range_values)
        result_df = pd.DataFrame(results, columns=['i', 'combined_mean', 'combined_std'])
        callback(result_df)

# Controller: Manages user input and updates the model
class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)

    def start_processing(self):
        self.view.show_processing()
        threading.Thread(target=self.run_model).start()

    def run_model(self):
        self.model.run_multiprocessing(self.processing_done)

    def processing_done(self, result_df):
        self.view.update_results(result_df)

# View: Handles the graphical interface
class View(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multiprocessing Example")
        self.geometry("400x300")
        self.controller = None
        self.create_widgets()

    def set_controller(self, controller):
        self.controller = controller

    def create_widgets(self):
        self.process_button = ttk.Button(self, text="Start Processing", command=self.on_process_button)
        self.process_button.pack(pady=20)
        
        self.result_text = tk.Text(self, height=10, width=40)
        self.result_text.pack(pady=20)

    def on_process_button(self):
        if self.controller:
            self.controller.start_processing()

    def show_processing(self):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Processing...")

    def update_results(self, result_df):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result_df.to_string())

# Main function to run the application
if __name__ == "__main__":
    model = DataModel()
    view = View()
    controller = Controller(model, view)
    view.mainloop()
