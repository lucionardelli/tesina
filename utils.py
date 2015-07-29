#!/usr/bin/env python
# -*- coding: UTF-8
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def add_to_position(xs, position, value=1):
    """
    given a list of numbers and a position, adds 1 to that position
    changing the same list
    """
    xs[position] += value

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

