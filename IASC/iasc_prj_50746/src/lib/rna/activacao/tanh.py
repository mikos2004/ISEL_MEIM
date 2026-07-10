import math
from .activacao import Activacao

class TanH(Activacao):
    def f(self, x):
        return math.tanh(x)
    
    def df(self, x):
        return 1 - math.tanh(x) ** 2