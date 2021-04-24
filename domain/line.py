class Line:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        self.slope = calculate_slope(self.p1[1] - self.p0[1], self.p1[0] - self.p0[0])
        self.y_intercept = self.p0[1] - self.slope * self.p0[0]

    def get_slope(self):
        return self.slope

    def get_y_intercept(self):
        return self.y_intercept

    def __str__(self):
        return 'Line: (' + str(self.p0) + ',' + str(self.p1) + ')'


def calculate_slope(diff_y, diff_x):
    if diff_x == 0:
        return 0
    else:
        return diff_y / diff_x
