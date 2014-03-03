
class Parent(object):
    def __init__(self):
        pass

    def deco(fun):
        def decorated(self, x):
            print("Calling decorated function...")
            x = fun(self, x)
            print("Exit...")
            return x
        return decorated

    @deco
    def f(self, x):
        raise NotImplementedError("Bla")


class Child(Parent):

    def f(self, x):
        self.x = x
        return x+1


if __name__ == "__main__":
    c = Child()
    p = Parent()
    
    print(c.f(1))
    
    print(p.f(1))