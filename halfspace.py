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

class Halfspace(Halfspace):
    """
    A halfspace defined by dot(normal, coords) + offset <= 0
    """
    def __init__(self, normal, offset):
        super(Halfspace,self).__init__(normal, offset)
        self.dim = len(normal)

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

    def __str__(self):
        header = "Halfspace in dimension {0}".format(self.dim)
        hs_repr = []
        for idx in xrange(self.dim):
            hs_repr.append("{0:.2f} x{1}".format(self.normal[idx], idx))
        hs_repr = ' + '.join(hs_repr)
        return "\n{0}\t {1} + {2:.2f} <= 0".format(header, hs_repr, self.offset)

    def inside(self, point):
        """
        Determines if given points is inside the halfspace
        Operator determines on wich side of the hyperspace
        is supposed to be

        Args:
            origin: point to check if is in the hyperplane
        """
        # For some reaons cannot import utils here...
        def almost_equal(f1, f2, tolerance=0.00001):
            return abs(f1 - f2) <= tolerance * max(abs(f1), abs(f2))
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

