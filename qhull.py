#!/usr/bin/env python
# -*- coding: UTF-8
from pyhull.convex_hull import ConvexHull
import pdb
from utils import check_argv

class Qhull(object):

    def __init__(self, points, verbose=False):
        self.points = set(points)
        self.vertices = set()
        self.qhull = set()
        self.simplices = []
        self.verbose = verbose

    def compute(self):
        self.qhull = ConvexHull(list(self.points))
        self.simplices = self.qhull.simplices
        self.vertices = self.qhull.vertices
        if self.verbose:
            print "Computed MCH with ", len(self.vertices)," points"
            print 'This are the points:'
            print(self.vertices)
            print "Computed MCH with ", len(self.simplices)," simplices"
            print 'This are them:'
            print(self.simplices)
        return len(self.qhull.vertices)


def main():
    usage = """
        Usage: ./qhull <points> [--debug][--verbose]
    """
    if not check_argv(sys.argv, minimum=1, maximum=4):
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
                qhull = Qhull(points)
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

