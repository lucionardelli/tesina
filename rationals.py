#!/usr/bin/env python
# -*- coding: UTF-8

# Float numbers will consider this much decimal part
TRUNCATE=2

from math import modf

from fractions import Fraction

def rationalize(num, max_denom=10):
    num = format(num, '.%dg'%TRUNCATE)
    rational = Fraction(num).limit_denominator(max_denom)
    return rational.numerator, rational.denominator

from utils import lcm, gcd

def make_common_divisor(numerators,denominators):
    if len(numerators) != len(denominators):
        raise Exception("Numerators (%s) must have the same length as "\
                "denominators (%s)"%(len(numerators),len(denominators)))
    this_lcm = lcm(*denominators)
    for idx, den in enumerate(denominators):
        numerators[idx] = (this_lcm / den) * numerators[idx]
    return numerators,[this_lcm]*len(numerators)
