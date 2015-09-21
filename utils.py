#!/usr/bin/env python
# -*- coding: UTF-8
from halfspace import Halfspace
from custom_exceptions import IncorrectOutput,CannotProject
import numpy as np

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

def parse_hs_output(output):
    """
     input: String of Hyperplane for each facet. The first line is the dimension.
     The second line is the number of facets. Each remaining line
     is the hyperplane's coefficients followed by its offset.
     output: (dimension,nbr_facets,[halfspaces])
    """
    try:
        dim = int(output.pop(0)) - 1
        facets_nbr = output.pop(0)
        prepare = [[float(i) for i in row.strip().split()]
                for row in output]
        facets = [Halfspace(out[:-1],out[-1]) for out in prepare]
    except:
        raise IncorrectOutput()
    return (dim, facets_nbr, facets)

def almost_equal(f1, f2, tolerance=0.00001):
    return abs(f1 - f2) <= tolerance * max(abs(f1), abs(f2))

def get_positions(eigenvector, cluster):
    evect = list(eigenvector)
    ret = []
    for val in cluster:
        ret.append(evect.index(val))
    return ret

def project(points, eigen, cluster, max_size=None):
    max_size = max_size or len(cluster)
    ret = []
    # Por cada variable en el cluster
    # busco el valor correspondiente en los puntos iniciales
    # y lo agrego a mi resultado
    # Los voy recorriendo en "orden de correlación"
    cluster.sort(key=lambda x: abs(x), reverse=True)
    positions = get_positions(eigen, cluster)
    # Nos limitamos al máximo numero de elementos en un cluster
    positions = positions[0:max_size]
    for point in points:
        proj_point = []
        for pos in positions:
            proj_point.append(point[pos])
        ret.append(proj_point)
    return map(tuple,ret)

def qhull_extend(qhull, eigen, cluster):
    """
     Given a qhull computed from a cluster (i.e. projection)
     "extended" it (making all the other variables zero)
     to the original dimension
    """
    # Nuevamente los odeno y busco la posición
    # en el eigenvector original. Luego "agrando"
    # el qhull en concordancia
    cluster.sort(key=lambda x: abs(x), reverse=True)
    positions = get_positions(eigen, cluster)
    qhull.extend_dimension(len(eigen), positions)
    return qhull
