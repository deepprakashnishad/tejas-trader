from technicals.technical import Technical


class Operator:

    name = ""

    def __init__(self, **kwargs):
        print(kwargs)

    def operate(self, index, technical1, technical2):
        pass

    def calculate_technicals(self, index, technical1, technical2=None):
        if technical2 is None:
            return technical1.calculate_series(index)
        else:
            return technical1.calculate_series(index), technical2.calculate_series(index)

    def get_index(self, index, series1, series2=None):
        if index > -1 and series2 is None:
            return index
        elif index > -1 and series2 is not None:
            return index, index
        elif series2 is None:
            return len(series1)-1
        else:
            return len(series1)-1, len(series2)-1
