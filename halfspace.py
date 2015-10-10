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
from rationals import integer_coeff

class Halfspace(Halfspace):
    """
    A halfspace defined by dot(normal, coords) + offset <= 0
    """
    def __init__(self, normal, offset, integer_vals=True):
        super(Halfspace,self).__init__(normal, offset)
        self.dim = len(normal)
        if integer_vals:
            try:
              self.integerify()
            except:
              import pdb;pdb.set_trace()
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
        hs_repr = ''
        for idx,coef in enumerate(self.normal):
            # Queremos dar vuelta el <= a 0 al imprimir
            if coef > 0:
                hs_repr += " - {0: >4} x{1: <3}".format(coef,idx)
            elif coef < 0:
                hs_repr += " + {0: >4} x{1: <3}".format(abs(coef),idx)
            else:
                # Los coeficientes 0 no los imprimimos
                pass
        if hs_repr.startswith(' + '):
            # El primer símbolo no va
            hs_repr = hs_repr[3:]

        if self.offset > 0:
            ti_repr = ' -  {0: >3}'.format(self.offset)
        elif self.offset < 0:
            ti_repr = ' +  {0: >3}'.format(self.offset)
        else:
            ti_repr = ''
        return "{0: <12}{1} {2} >= 0".format(header, hs_repr, ti_repr)

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

            integerified = integer_coeff(self.normal+[self.offset])

            self.offset = integerified[-1]
            self.normal = integerified[:-1]
        else:
            self.offset = int(self.offset)
            self.normal = map(int,self.normal)

