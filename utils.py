#!/usr/bin/env python
# -*- coding: UTF-8
from custom_exceptions import IncorrectOutput,CannotProject
import numpy as np

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def check_argv(argv, minimum=1, maximum=1):
    """
        Ensures that the there are at least minimum and at most maximum strings
        in argv
    """
    if maximum < minimum:
        t = minimum
        minimum = maximum
        maximum = t
    ret = minimum < len(argv) < maximum + 1
    return ret and all(map(lambda x: type(x) == type(''), argv))

def almost_equal(f1, f2, tolerance=0.00001):
    return abs(f1 - f2) <= tolerance * max(abs(f1), abs(f2))

def get_positions(eigenvector, cluster):
    # We ensure that first argument is a list-like
    evect = list(eigenvector)
    ret = []
    for val in cluster:
        ret.append(evect.index(val))
    return ret

def my_round(point):
    """
        Custom "round". It doesn't actually round numbers.
        It truncate it if it is "almost" an integer
        If it's positive it returns the ceil and if its
        negative it returns the floor because this
        This behaviour always "adds" points to a model
    """
    ret =int(point)
    if not almost_equal(point,ret):
        ret = point > 0 and int(np.ceil(point)) or int(np.floor(point))
    return ret

def __gcd_two(num1,num2=0):
    while num2:
        num1, num2 = num2, num1%num2
    return num1 or 1

def gcd(*args):
    return reduce(__gcd_two, args)

def __lcm_two(num1,num2=1):
    return num1 * num2 / __gcd_two(num1,num2)

def lcm(*args):
    return reduce(__lcm_two, args)
