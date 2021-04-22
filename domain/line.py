class Line:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

    def get_slope(self):
        return self.p1[1] - self.p0[1] / self.p1[0] - self.p0[0]

    def get_y_intercept(self):
        slope = self.get_slope()
        return self.p0[1] - slope * self.p0[0]

    def __str__(self):
        return 'Line: (' + str(self.p0) + ',' + str(self.p1) + ')'
