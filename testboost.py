#!/usr/bin/env python

import foobar

class Foo(foobar.baz):
    def pure(self, n):
        return n

c = Foo()

print(c.pure(5))
print(c.calls_pure(5))


