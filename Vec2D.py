import math

class Vec2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return self.x*other.x + self.y*other.y

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return '(%g, %g)' % (self.x, self.y)

    def __ne__(self, other):
        return not self.__eq__(other)  # reuse __eq__

    def unit(self):
        m = self.get_mag()
        if m == 0: return self
        
        x = self.x/m
        y = self.y/m
        return Vec2D(x, y)

    def get_mag(self):
        return math.sqrt((self.x*self.x)+(self.y*self.y))

    def set_mag(self, mag):
        unit = self.unit()
        x = unit.x*mag
        y = unit.y*mag
        return Vec2D(x,y)

    def rotate(self, angle):
        x = math.cos(angle)*self.x-math.sin(angle)*self.y
        y = math.sin(angle)*self.x+math.cos(angle)*self.y
        return Vec2D(x,y)

    def mult(self, num):
        return Vec2D(self.x * num, self.y * num)

def getVec2DFromAngle(angle):
    return Vec2D(math.cos(angle), math.sin(angle))

def get_vec2d_from_2_points(x1, y1, x2, y2):
    return Vec2D(x2-x1, y2-y1)

if __name__ == '__main__':
    v = vec2D(5,5)
    v2 = vec2D(1,1)

    print(v, v2)
    print()