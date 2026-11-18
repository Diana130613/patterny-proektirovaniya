class MatrixIterator:
    def __init__(self, matrix):
        self.matrix = matrix
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= self.matrix.rows * self.matrix.columns:
            raise StopIteration
        row, column = divmod(self.index, self.matrix.columns)
        self.index += 1
        return row, column, self.matrix.data[row][column]


def sign_counts(matrix):
    positive = negative = zero = 0
    for row, column, value in matrix:
        if value > 0:
            positive += 1
        elif value < 0:
            negative += 1
        else:
            zero += 1
    return positive, negative, zero
