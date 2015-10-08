# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 20:57:08 2015

@author: burger
"""

import turtle
import numpy as np

from time import sleep


GRAVITATIONAL_CONSTANT = 100


class Collision(Exception):
    pass


class Body(object):
    def __init__(self):
        self.x = np.asarray([[1.0], [0.0]])
        self.v = np.asarray([[0.0], [1.0]])
        self.m = 1.0

    def step(self, objs, dt=1):
        a = acceleration(self.x, objs)
        #print(np.concatenate((self.x, self.v, a), axis=1))
        old_v = self.v
        self.v += dt*a
        self.x += dt*(self.v + old_v)/2
        #self.x += dt*self.v


def acceleration(x, objs):
    a = np.zeros_like(x)

    for obj in objs:
        d = -(x - obj.x)
        abs_d = np.square(d).sum(axis=0)
        if abs_d < 1e-5:
            raise Collision()

        abs_a = GRAVITATIONAL_CONSTANT * obj.m / abs_d
        a += abs_a * d/abs_d

    return a


def main():
    dt = .1
    turtle.Screen()
    t = turtle.Turtle()

    b = Body()
    b.x *= 30
    b.v *= 100

    b2 = Body()
    b2.x *= 0
    b2.m = 95000
    stars = [b2]

    t.up()
    last_x = 0
    last_y = 0
    for i in range(10000):
        sleep(.05)
        x = float(b.x[0, 0])
        right = x - last_x
        last_x = x
        #print("going {} to the right".format(right))
        t.forward(right)
        t.left(90)
        y = float(b.x[1, 0])
        up = y - last_y
        last_y = y
        #print("going {} upwards".format(up))
        t.forward(up)
        t.right(90)
        t.down()
        b.step(stars, dt=dt)


if __name__ == "__main__":
    main()
