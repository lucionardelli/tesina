#!/usr/bin/env python
# -*- coding: UTF-8
from pyhull.convex_hull import ConvexHull
from pyhull import qconvex
import pdb
from utils import check_argv, get_positions
from halfspace import Halfspace
from custom_exceptions import IncorrectOutput, CannotGetHull

class Qhull(object):

    def __init__(self, points, verbose=False):
        self.points = set(points)
        self.vertices = set()
        self.__qhull = None
        self.simplices = []
        self.facets = []
        self.verbose = verbose

    def __parse_hs_output(self, output):
        """
         input: Output string for ConvexHull
            The first line is the dimension.
            The second line is the number of facets.
            Each remaining line is the hyperplane's coefficient
                followed by its offset.
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

    def compute_vertices(self):
        self.__qhull = ConvexHull(list(self.points))
        self.simplices = self.__qhull.simplices
        self.vertices = self.__qhull.vertices
        self.dim = self.__qhull.dim
        if self.verbose:
            print "Computed MCH with ", len(self.vertices)," points"
            print 'This are the points:'
            print(self.vertices)
            print "Computed MCH with ", len(self.simplices)," simplices"
            print 'This are them:'
            print(self.simplices)
        return len(self.vertices)

    def compute_hiperspaces(self):
        output = qconvex('n',list(self.points))
        try:
            dim, facets_nbr, facets = self.__parse_hs_output(output)
        except IncorrectOutput:
            raise CannotGetHull()
        self.dim = dim
        self.facets = facets
        if self.verbose:
            print "Computed MCH with ",facets_nbr," halfspaces"
            print 'This are them:\n'
            for facet in self.facets:print facet
        return self.dim

    def union(self, facets):
        """
         Merge hull to a list of facets
        """
        fdim = None
        for facet in facets:
            if fdim is None:
                fdim = facet.dim
            else:
                assert fdim == facet.dim, "Not all facets to be merge hava the"\
                        " same dimension!"
        # If fdim is None the facets to merge is empty. We can always do that
        if fdim is not None and self.dim != fdim:
            raise ValueError("Convex Hulls and facets must live in the same"\
                    " dimension!")
        self.facets = list(set(self.facets) | set(facets))

    def is_inside(self,outsider):
        ret = True
        for facet in self.facets:
            if not facet.inside(outsider):
                ret = False
                break
        return ret

    def restrict_to(self, outsider):
        facets = list(self.facets)
        popped = 0
        for idx,facet in enumerate(self.facets):
            if not facet.inside(outsider):
                facets.pop(idx - popped)
                popped += 1
        self.facets = facets

    def extend_dimension(self, dim, ext_dict):
        """
            dim: the dimension to exetend to
            ext_dict: a list of the "old" points position
                      in the new qhull (given in order)
        """
        self.dim = dim
        for facet in self.facets:
            facet.extend_dimension(dim, ext_dict)

    def extend(self, eigen, cluster):
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
        self.extend_dimension(len(eigen), positions)


def main():
    usage = 'Usage: ./qhull <points> [--debug][--verbose]'
    if not check_argv(sys.argv, minimum=1, maximum=5):
        print usage
        ret =  -1
    else:
        ret = 0
        try:
            from os.path import isfile
            import ast
            if '--debug' in sys.argv:
                pdb.set_trace()
            try:
                if isfile(sys.argv[1]):
                    print sys.argv[1], 'assumed to be a file'
                    with open(sys.argv[1], 'r') as ffile:
                            points = ffile.readline()
                else:
                    points = sys.argv[1]
                points = ast.literal_eval(points)
                if '--verbose' in sys.argv:
                    print "Se colectaron ", len(points), " puntos"
                points = set(map(lambda x: tuple(x),points))
                if '--verbose' in sys.argv:
                    print "Se colectaron ", len(points), " puntos DIFERENTES"
            except:
                ret = -1
                print "We are sorry. We weren't able to read the points"
            else:
                qhull = Qhull(points, verbose='--verbose' in sys.argv)
                point_qty = qhull.compute()
                print "Computed MCH with ", point_qty," points"
                if '--verbose' in sys.argv:
                    print 'This are the points:'
                    print(qhull.vertices)
        except Exception, err:
            ret = 1
            if hasattr(err, 'message'):
                print 'Error: ', err.message
            else:
                print 'Error: ', err
    return ret

if __name__ == '__main__':
    import sys, traceback
    try:
        main()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

