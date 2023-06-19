

class Namer:
    def __init__(self,initial=""):
        self.name = initial
        self.charadd ="A"
    def current_name(self):
        return self.name+self.charadd
    def next_name(self):
        newchar = ord(self.charadd)+1
        if newchar>90:
            self.name= self.name+self.charadd
            self.charadd ="A"
        else:
            self.charadd =chr(newchar)
