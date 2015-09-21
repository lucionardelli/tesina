#!/usr/bin/env python
# -*- coding: UTF-8
from qhull import Qhull
from parser import XesParser
from corrmatrix import CorrMatrix
from utils import check_argv, project, qhull_extend
import pdb
import time
import numpy as np
from random import sample

from halfspace import Halfspace
from custom_exceptions import CannotGetHull, WrongDimension
from kmeans import two_means

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
                except (CannotGetHull,WrongDimension):
                    tries -= 1
                    if tries == 0:
                        raise Exception('Cannot get MCH. Maybe doing *TOO*'\
                                ' small sampling')
        return qhull
    return do_sampling

def projection(func):
    def do_projection(self, points, *args, **kwargs):
        # Calculamos la matrix de correlaciones
        points = np.array(list(points))
        if self.proj_size is None:
            # Si el máximo es None es porque no se desea hacer projection
            qhull = func(self, points, *args, **kwargs)
        else:
            # Hacemos projection
            corr = CorrMatrix(points)
            facets = []
            qhull = None
            while True:
                # Hacemos una lista de pares (valor, posicion)
                tup = [(abs(y),x) for x,y in enumerate(corr.eigenvalues)]
                # la ordenamos ascendentemente por el valor
                # y la iteramos (solo nos interesan los índices ordenadamente)
                tup.sort(reverse=True)
                # Si 'tup' no tiene al menos un elemento algo anduvo mal...
                # es como si no tuviesemos eigen-valores en la matriz
                # Tomamos el eigenvector correspondiente al mayor eigenvalor
                # ya que se espera que sea el que más info tiene sobre
                # correlaciones
                _,idx = tup[0]
                eigen = corr.eigenvector[:,idx]
                # tomamos la fila correspondiente al líder
                # (más grande en valor absoluto)
                # en la matriz de correlación
                eigen_abs = map(abs,eigen)
                leader = eigen_abs.index(max(eigen_abs))
                leader_row = corr.matrix[leader]
                #solo utilizamos el cluster de mayor correlación
                cluster0, cluster1 = two_means(leader_row)
                if len(cluster1) <= 1:
                    break
                pts_proj = project(points, leader_row, cluster1,
                        max_size=self.samp_size)
                qhull = func(self, pts_proj, *args, **kwargs)
                # Extendemos a la dimensión original
                qhull = qhull_extend(qhull, leader_row, cluster1)
                # Agregamos las facetas que ya calculamos
                qhull.union(facets)
                facets = qhull.facets
                # Actualizamos la matriz poniendo en 0 los valores usados
                corr.update(leader, cluster1)
        return qhull
    return do_projection

class PacH(object):

    def __init__(self, filename, verbose=False,
            samp_num=1, samp_size=None,
            proj_size=None, proj_connected=True):
        self.filename = filename
        self.dim = 0
        self.pv_traces = []
        self._qhull = None
        self._facets = []
        self.verbose = verbose
        # Sampling configuration
        # At least we need one "sample"
        self.samp_num = max(samp_num,1)
        self.samp_size = samp_size
        # Projection configuration
        # If proj_size is None, do not do projection
        self.proj_size = proj_size
        self.proj_connected = proj_connected

    def parse(self):
        if self.verbose:
            print 'Starting parse\n'
            start_time = time.time()
        parser = XesParser(self.filename, verbose=self.verbose)
        parser.parikhs_vector()
        self.pv_traces = parser.pv_traces
        self.pv_set = parser.pv_set
        self.pv_array = parser.pv_array
        self.dim = parser.dim
        if self.verbose:
            print 'Parse done\n'
            elapsed_time = time.time() - start_time
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'

    def get_sample(self):
        points = set()
        for p_vect in sample(self.pv_set,
                self.samp_size or len(self.pv_set)):
            points.add(tuple(p_vect))
        return points

    @property
    def qhull(self):
        return self._qhull or self.get_qhull(self.pv_array)

    @property
    def facets(self):
        return self._facets or self.qhull.facets

    @sampling
    @projection
    def get_qhull(self, points):
        points = set(map(tuple, points))
        qhull = Qhull(points) # We'll hande the vebose ourselves
        qhull.compute_hiperspaces()
        return qhull

    def model(self, points=None):
        if self.verbose:
            print 'Starting modeling\n'
            start_time = time.time()
        if self.verbose:
            print "Ended with MCH with ",len(self.facets)," halfspaces"
            print 'This are them:\n'
            for facet in self.facets:print facet
        if self.verbose:
            elapsed_time = time.time() - start_time
            print 'Modeling done\n'
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'

    def point_model(self):
        if self.verbose:
            print 'Starting modelling\n'
            start_time = time.time()
        self.qhull = Qhull(self.pv_set, verbose=self.verbose)
        ret = self.qhull.compute()
        if self.verbose:
            print 'Modelling done\n'
            elapsed_time = time.time() - start_time
            print 'MCH points: {2}\n'\
                'Diferent parsed points: {0}\n'\
                'Parsed points dimension: {1}\n'.format(ret, len(self.dim),
                self.parser.dimension)
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'

    def pach(self):
        self.parse()
        self.model()


def main():
    usage = 'Usage: ./pach <XES filename> [--debug][--verbose]'\
        ' [--sampling [<number of samplings>] [<sampling size>]]'\
        ' [--projection [<max group size>] [<connected model>]]'
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
            proj_size = None
            proj_connected = True
            if '--projection' in sys.argv or '-p' in sys.argv:
                # None indicates not to do projection.
                # False indicates heuristic limit
                proj_size = False
                proj_idx = '-p' in sys.argv and sys.argv.index('-p') or\
                    sys.argv.index('--projection')
                try:
                    proj_size = int(sys.argv[proj_idx+1])
                except:
                    pass
                try:
                    proj_connected = int(sys.argv[proj_idx+2])
                except:
                    pass

            pach = PacH(filename, verbose=('--verbose' in sys.argv),
                    samp_num=samp_num, samp_size=samp_size,
                    proj_size=proj_size, proj_connected=proj_connected)
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

