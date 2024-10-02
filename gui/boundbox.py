class BoundBox:
    def __init__(self, parent, x:float, y:float, w:float, h:float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.parent = parent
        self.order = self.parent.order
    def contains(self, x, y):
        # print(self.y, self.y + self.h)
        return ((self.y <=y < self.y + self.h) and (self.x <= x < self.x + self.w))

    def get_area(self):
        return abs((self.w - self.x)*(self.h - self.y))
    
    def __repr__(self):
        return "<BoundBox::[{} {} {} {}]>".format(self.x, self.y, self.w, self.h)
    

class BoundCapsule(BoundBox):
    def __init__(self, parent, x1:float, y1:float, x2:float, y2:float, r:float):
        super().__init__(parent, x1, y1, x2, y2)
        self.r = r
    
    def contains(self, x, y):
        ba2 = (self.x - self.w)**2 + (self.y - self.h)**2
        ba = (ba2)**(0.5)
        h = ((x - self.x)*(self.w - self.x) + (y - self.y)*(self.h - self.y))/ba2
        h = min(1, max(0, h))
        d = (x - self.x) - h*(self.w - self.x), (y - self.y) - h*(self.h - self.y)
        s = (d[0]*d[0] + d[1]*d[1])**(0.5)
        return s < self.r
        
