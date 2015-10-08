#!/usr/bin/python2

d = dict()
print(d)


class MyClass(object):
    d['a'] = 1
    print(d)

    def someMethod(self):
        pass


if __name__ == "__main__":
    print(d)
    d['a'] = 2
    m = MyClass()
    print(d)
