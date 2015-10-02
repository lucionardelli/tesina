#!/usr/bin/env python
# -*- coding: UTF-8
"""
This module inherits pyhull halfspace class to add basic functionality
that the other modules lacks of
"""

__author__ = "Lucio Nardelli"
__version__ = "0.1"
__maintainer__ = "Lucio Nardelli"
__email__ = "lucio (at) fceia.unr.edu.ar"
__date__ = "August 27, 2015"

from pyhull.halfspace import Halfspace

import numpy as np

from utils import almost_equal, gcd
from rationals import rationalize, make_common_divisor

class Halfspace(Halfspace):
    """
    A halfspace defined by dot(normal, coords) + offset <= 0
    """
    def __init__(self, normal, offset, integer_vals=True):
        super(Halfspace,self).__init__(normal, offset)
        self.dim = len(normal)
        if integer_vals:
            self.integerify()

    def __hash__(self):
        return hash(str(self.normal + [self.offset]))

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.__str__()

    def __contains__(self, element):
        return self.inside(element)

    def __str__(self):
        header = "HS dim {0}".format(self.dim)
        hs_repr = []
        for idx in xrange(self.dim):
            hs_repr.append("{0: >4} x{1: <3}".format(self.normal[idx], idx))
        hs_repr = ' + '.join(hs_repr)
        return "{0: <12}{1} + {2: >3} <= 0".format(header, hs_repr, self.offset)

    def __fstr__(self):
        header = "HS in dim {0}".format(self.dim)
        hs_repr = []
        for idx in xrange(self.dim):
            hs_repr.append("{0:.2f} x{1}".format(self.normal[idx], idx))
        hs_repr = ' + '.join(hs_repr)
        return "{0}\t{1} + {2:.2f} <= 0".format(header, hs_repr, self.offset)

    def inside(self, point):
        """
        Determines if given points is inside the halfspace
        Operator determines on wich side of the hyperspace
        is supposed to be

        Args:
            origin: point to check if is in the hyperplane
        """
        try:
            eq_res = np.dot(self.normal,point) + self.offset
        except Exception, err:
            raise WrongDimension()
        return eq_res < 0.0 or almost_equal(eq_res, 0.0, tolerance=0.0001)

    def extend_dimension(self, dim, ext_dict):
        """
            dim: the dimension to exetend to
            ext_dict: a list of the "old" points position
                      in the new qhull (given in order)
        """
        self.dim = dim
        normal = []
        for axis in xrange(dim):
            if axis in ext_dict:
                # El eje pertenece a una dimensión "de los viejas"
                idx = ext_dict.index(axis)
                normal.append(self.normal[idx])
            else:
                normal.append(0)
        self.normal = normal

    def axis_intersection(self, axis):
        # Buscamos la intersección del hiperespacio con el eje 'axis'
        ret = 0
        if self.normal[axis]:
            ret = (-1 * self.offset) / self.normal[axis]
        return ret

    def integerify(self):
        # Si alguno de los valores no es un entero,
        # buscamos una representación equivalente
        # del hiperespacio a valores enteros
        if any(map(lambda x: not x.is_integer(), self.normal)):
            numerators = []
            denominators = []
            for idx in xrange(self.dim):
                num, den = rationalize(self.normal[idx])
                numerators.append(num)
                denominators.append(den)
            num, den = rationalize(self.offset)
            numerators.append(num)
            denominators.append(den)

            numerators, denominators = make_common_divisor(numerators,
                                                           denominators)
            # Todas las fracciones poseen el mismo denominador
            # Por lo que puedo multiplar el hiperplano por el denominador
            # Y el hiperplano no debería cambiar

            # Intentamos mantener los valores lo más pequeños posible
            # En general no debería hacer nada
            use_gcd = abs(gcd(*numerators))
            if use_gcd != 1:
                numerators = map(lambda x: x/use_gcd, numerators)

            self.offset = numerators[-1]
            self.normal = numerators[:-1]
        else:
            self.offset = int(self.offset)
            self.normal = map(int,self.normal)

