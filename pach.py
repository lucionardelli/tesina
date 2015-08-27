#!/usr/bin/env python
# -*- coding: UTF-8
from qhull import Qhull
from parser import XesParser
from utils import check_argv
import pdb
import time
from random import sample
from halfspace import Halfspace
from custom_exceptions import CannotGetHull, WrongDimension

class PacH(object):

    def __init__(self, filename, verbose=False,
            samp_num=1, samp_size=None):
        self.filename = filename
        self.dim = 0
        self.pv_list = []
        self.facets = []
        self.verbose = verbose
        # At least we need one "sample"
        self.samp_num = max(samp_num,1)
        self.samp_size = samp_size

    def parse(self):
        if self.verbose:
            print 'Starting parse\n'
            start_time = time.time()
        parser = XesParser(self.filename, verbose=self.verbose)
        parser.parikhs_vector()
        self.pv_list = parser.pv_list
        self.points = parser.points
        self.dim = parser.dim
        if self.verbose:
            print 'Parse done\n'
            elapsed_time = time.time() - start_time
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'

    def get_sample(self):
        # Por ahora lo hago una sola vez, creo que eso debería hacer esta func
        #for samp in xrange(self.samp_num):
            points = set()
            for trace_idx in sample(self.pv_list,
                    self.samp_size or len(self.pv_list)):
                trace = self.pv_list[trace_idx]
                for point in trace:
                    points.add(tuple(point))
            yield points

    def do_sampling(self):
        seen_points = set()
        facets = []
        # When sampling, it can be the case that the calculated
        # sample is insuficient to calculate MCH, so try a few
        # times before actually raising error
        tries = 3 if self.samp_size else 1
        while tries:
            try:
                for points in self.get_sample():
                    seen_points |= points
                    qhull = Qhull(points)# We'll hande the vebose ourselves
                    qhull.compute_hs()
                    # Agregamos las facetas que ya calculamos
                    qhull.union(facets)
                    # Los puntos no considerados restringen las facetas
                    for outsider in self.points - seen_points:
                        qhull.restrict_to(outsider)
                    facets = qhull.facets
                    tries = 0
            except (CannotGetHull,WrongDimension):
                tries -= 1
                if tries == 0:
                    raise Exception('Cannot get MCH. Maybe doing *TOO* small'\
                            ' sampling')
        self.facets = facets
        if self.verbose:
            print "After sampling:\n"
            print "Ended with MCH with ",len(self.facets)," halfspaces"
            print 'This are them:\n'
            for facet in self.facets:print facet
        return len(seen_points)

    def model(self, points=None):
        if self.verbose:
            print 'Starting modeling\n'
            start_time = time.time()
        ret = self.do_sampling()
        if self.verbose:
            elapsed_time = time.time() - start_time
            print 'Modeling done\n'
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'
        return ret

    def point_model(self):
        if self.verbose:
            print 'Starting modelling\n'
            start_time = time.time()
        self.qhull = Qhull(self.parser.points, verbose=self.verbose)
        ret = self.qhull.compute()
        if self.verbose:
            print 'Modelling done\n'
            elapsed_time = time.time() - start_time
            print 'MCH points: {2}\n'\
                'Diferent parsed points: {0}\n'\
                'Parsed points dimension: {1}\n'.format(ret, len(self.qhull.points),
                self.parser.dimension)
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'

    def pach(self):
        self.parse()
        self.model()


def main():
    usage = 'Usage: ./pach <XES filename> [--debug][--verbose]'\
        ' [--sampling [<number of samplings>] [<sampling size>]]'
    if not check_argv(sys.argv, minimum=1, maximum=7):
        print usage
        ret = -1
    else:
        ret = 0
        try:
            from os.path import isfile
            if '--debug' in sys.argv:
                pdb.set_trace()
            filename = sys.argv[1]
            if not filename.endswith('.xes'):
                print filename, ' does not end in .xes. It should...'
                raise Exception('Filename does not end in .xes')
            if not isfile(filename):
                raise Exception("El archivo especificado no existe")
            samp_num = 1
            samp_size = None
            if '--sampling' in sys.argv or '-s' in sys.argv:
                samp_idx = '-s' in sys.argv and sys.argv.index('-s') or\
                    sys.argv.index('--sampling')
                try:
                    samp_num = int(sys.argv[samp_idx+1])
                except:
                    pass
                try:
                    samp_size = int(sys.argv[samp_idx+2])
                except:
                    pass
            pach = PacH(filename, verbose=('--verbose' in sys.argv),
                    samp_num=samp_num, samp_size=samp_size)
            pach.pach()
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

