#!/usr/bin/env python
# -*- coding: UTF-8
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def add_to_position(xs, position, value=1):
    """
    given a list of numbers and a position, adds 1 to that position
    """
    return xs[:position] + [xs[position] + value] + xs[position+1:]

