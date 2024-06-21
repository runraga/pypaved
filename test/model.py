import multiprocessing as mp
import time

class Model:
    def __init__(self):
        self.progress = mp.Value('i', 0)
        self.total = 1000000000  # One billion numbers
        self.running = mp.Value('b', True)
        self.pool = mp.Pool(mp.cpu_count())
        

    def start_processing(self):
        self.running.value = True
        self.progress.value = 0
        self.pool.apply(self.process_data)


    def process_data(self):
        batch_size = 1000000  # Process a million numbers at a time
        while self.progress.value < self.total and self.running.value:
            time.sleep(0.1)  # Simulate some time delay in processing
            
            self.progress.value += batch_size
            
        if self.progress.value >= self.total:
            self.running.value = False
           


    def print_progress(self, progress):
        percent = (progress / self.total) * 100
        print(f"Progress: {percent:.2f}%")




if __name__ == '__main__':
    model = Model()

    try:
        model.start_processing()
        while model.running.value:
            time.sleep(0.5)  # Main thread can do other work or just wait

    except KeyboardInterrupt:
        print("Stopping the process...")
        print("Process stopped.")
