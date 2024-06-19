class RowManager:
    def __init__(self):
        self.current_row = 0

    def get_row_number(self):

        return self.current_row

    def increment_row(self):
        self.current_row += 1
