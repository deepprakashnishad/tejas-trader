from technicals.operators.operator import Operator
import math


class GreaterThan(Operator):
    def __init__(self, **kwargs):
        self.name = "GreaterThan"

    def operate(self, index, technical1, technical2, limit=None):
        series1, series2 = self.calculate_technicals(index=index, technical1=technical1, technical2=technical2)
        index1, index2 = self.get_index(index, series1, series2)
        if limit is None:
            return series1[index1] > series2[index2]
        else:
            return series2[index2] + limit > series1[index1] > series2[index2]


class LessThan(Operator):

    def __init__(self, **kwargs):
        self.name = "LessThan"

    def operate(self, index, technical1, technical2, limit=None):
        series1, series2 = self.calculate_technicals(index=index, technical1=technical1, technical2=technical2)
        index1, index2 = self.get_index(index, series1, series2)
        if limit is None:
            return series1[index1] < series2[index2]
        else:
            return series2[index2] - limit < series1[index1] < series2[index2]


class EqualTo(Operator):

    def __init__(self, **kwargs):
        self.name = "EqualTo"

    def operate(self, index, technical1, technical2, limit=None):
        series1, series2 = self.calculate_technicals(index=index, technical1=technical1, technical2=technical2)
        index1, index2 = self.get_index(index, series1, series2)
        if limit is None:
            return series1[index1] == series2[index2]
        else:
            return abs(series2[index2] - series1[index1]) <= abs(limit)


class CrossesBelow(Operator):
    def __init__(self, **kwargs):
        self.period_before_crossover = kwargs['period_before_crossover']
        self.period_after_crossover = kwargs['period_after_crossover']

    def operate(self, index, technical1, technical2, limit=None):
        series1, series2 = self.calculate_technicals(index=index, technical1=technical1, technical2=technical2)
        for i in range(0, self.period_before_crossover):
            if series1[index - i - self.period_after_crossover] > series1[index - i - self.period_after_crossover - 1] \
                    or series1[index - self.period_after_crossover - i] \
                    < series2[index - self.period_after_crossover - i]:
                return False

        for i in range(0, self.period_after_crossover):
            if series1[index - i] > series1[index - i - 1] or series1[index - i] > series2[index - i]:
                return False
        return True


class CrossesAbove(Operator):
    def __init__(self, **kwargs):
        self.period_before_crossover = kwargs['period_before_crossover']
        self.period_after_crossover = kwargs['period_after_crossover']

    def operate(self, index, technical1, technical2, limit=None):
        series1, series2 = self.calculate_technicals(index=index, technical1=technical1, technical2=technical2)
        for i in range(0, self.period_before_crossover):
            if series1[index - i - self.period_after_crossover] < series1[index - i - self.period_after_crossover - 1] \
                    or series1[index - self.period_after_crossover - i] > \
                    series2[index - self.period_after_crossover - i]:
                return False

        for i in range(0, self.period_after_crossover):
            if series1[index - i] < series1[index - i - 1] or series1[index - i] < series2[index - i]:
                return False
        return True


class Rising(Operator):
    is_unary = True

    def __init__(self, **kwargs):
        self.period = kwargs['period']
        self.name = "Rising"

    def operate(self, index, technical1, technical2=None, limit=None):
        series = technical1.calculate_series(index)
        index = self.get_index(index, series)
        for i in range(0, int(self.period)):
            if math.isnan(series[index - i]) or math.isnan(series[index - i - 1]) \
                    or series[index - i - 1] > series[index - i]:
                # if technical1.calculate(index-1) > technical1.calculate(index):
                return False
        return True


class Sinking(Operator):
    is_unary = True

    def __init__(self, **kwargs):
        self.period = kwargs['period']

    def operate(self, index, technical1, technical2, limit=None):
        series = technical1.calculate_series(index)
        index = self.get_index(index, series)
        for i in range(0, int(self.period)):
            if math.isnan(series[index - i]) \
                    or math.isnan(series[index - i - 1]) \
                    or series[index-i] > series[index-i-1]:
                return False
        return True


class Narrow(Operator):
    is_unary = True

    def __init__(self, **kwargs):
        self.period = kwargs['period']

    def operate(self, index, technical1, limit=None):
        series = technical1.calculate_series(index)
        current = series[0]
        for i in range(0, self.period):
            if current > series[i]:
                return False
        return True

# class BounceDownwards(Operator):
# class BounceUpwards(Operator):
# Support and Resistance
# (mx+c) straight line for find support and resistance
