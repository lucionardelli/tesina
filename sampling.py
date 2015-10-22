#!/usr/bin/env python
# -*- coding: UTF-8

from custom_exceptions import CannotGetHull, WrongDimension, CannotIntegerify

def sampling(func):
    def do_sampling(self, points, *args, **kwargs):
        seen_points = set()
        facets = []
        for _ in xrange(self.samp_num):
            # When sampling, it can be the case that the calculated
            # sample is insuficient to calculate MCH, so try a few
            # times before actually raising error
            tries = 3 if self.samp_size else 1
            while tries:
                try:
                    points = self.get_sample()
                    seen_points |= points
                    qhull = func(self, points, *args, **kwargs)
                    # Agregamos las facetas que ya calculamos
                    qhull.union(facets)
                    # Los puntos no considerados restringen las facetas
                    for outsider in self.pv_set - seen_points:
                        qhull.restrict_to(outsider)
                    facets = qhull.facets
                    tries = 0
                except CannotIntegerify, err:
                    raise err
                except (CannotGetHull,WrongDimension), err:
                    tries -= 1
                    if tries == 0:
                        print 'Cannot get MCH. Maybe doing *TOO*'\
                                ' small sampling'
                        raise err
        return qhull
    return do_sampling