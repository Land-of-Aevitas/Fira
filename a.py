import re
import gc

class C1(object):
    def __init__(self) -> None:
        pass
    
    def def1(self):
        print('def1')

class C2(C1):
    def __init__(self) -> None:
        super().__init__()
        
    def def2(self):
        print('def2')


c1 = C1()
#c1.def1()

c2 = C2()
print(issubclass(C2, C1))