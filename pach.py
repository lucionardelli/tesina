#!/usr/bin/env python
# -*- coding: UTF-8
from qhull import Qhull
from parser import XesParser, AdHocParser
from corrmatrix import CorrMatrix
from utils import (check_argv, almost_equal, my_round,
                    get_positions, rotate_dict)
import pdb
import time
import numpy as np
from random import sample

from halfspace import Halfspace
from custom_exceptions import CannotGetHull, WrongDimension, CannotIntegerify
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
            corr2 = corr.copy()
            facets = []
            qhull = None
            projections = {}
            proj_count = 0
            while True:
                proj_count += 1
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
                _, cluster1 = two_means(leader_row,max_size=self.proj_size)
                if len(cluster1) <= 1:
                    if qhull is not None:
                        break
                    else:
                        # Aunque la proyección sea mala,
                        # tenemos que hacer al menos una.
                        cluster0,cluster1 = two_means(leader_row)
                        cluster1.append(max(cluster0))
                pts_proj, projected = self.project(points, leader_row, cluster1)
                projections[proj_count] = projected
                qhull = func(self, pts_proj, *args, **kwargs)
                # Extendemos a la dimensión original
                qhull.extend(leader_row, cluster1)
                # Agregamos las facetas que ya calculamos
                qhull.union(facets)
                facets = qhull.facets
                # Actualizamos la matriz poniendo en 0 los valores usados
                corr.update(leader, cluster1)
            if self.proj_connected:
                # Intentamos hacer que el modelo sea conexo
                # con este algoritmo heurístico
                last_con_line = None
                while True:
                    p0,p1,cor0,cor1 = corr2.closest_points(projections)
                    if not (any(cor0) and any(cor1)):
                        break
                    con_line = cor0 + cor1
                    if last_con_line is not None and last_con_line == con_line:
                        break
                    else:
                        last_con_line = con_line
                    _, cluster1 = two_means(con_line,max_size=self.proj_size)
                    if len(cluster1) <= 1:
                        continue
                    pts_proj, projected = self.project(points, con_line, cluster1)
                    qhull = func(self, pts_proj, *args, **kwargs)
                    # Extendemos a la dimensión original
                    qhull.extend(con_line, cluster1)
                    # Agregamos las facetas que ya calculamos
                    qhull.union(facets)
                    facets = qhull.facets
                    # Actualizamos la matriz poniendo en 0 los valores usados
                    corr2.update(p0, cluster1)
                    corr2.update(p1, cluster1)
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
# This is not working at the moment
        self.proj_connected = proj_connected and False

    def parse(self):
        if self.verbose:
            print 'Starting parse\n'
            start_time = time.time()
        if self.filename.endswith('.xes'):
            parser = XesParser(self.filename)
        elif self.filename.endswith('.txt'):
            parser = AdHocParser(self.filename)
        parser.parikhs_vector()
        self.event_dictionary = rotate_dict(parser.event_dictionary)
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

    def project(self, points, eigen, cluster):
        """
            Project the points into the cluster
            given by the value of the points
            in the eigen vector
            returns the projection and the list of projected points indexes
        """
        max_size = self.samp_size or len(cluster)
        ret = []
        # Por cada variable en el cluster
        # busco el valor correspondiente en los puntos iniciales
        # y lo agrego a mi resultado
        # Los voy recorriendo en "orden de correlación"
        cluster.sort(key=lambda x: abs(x), reverse=True)
        positions = get_positions(eigen, cluster)
        # Cuando queremos conectar las proyecciones pasamos una union
        # de dos eigenvectors, por lo que necesitamos el moulo dim
        # para obtener la pos correcta
        # Nos limitamos al máximo numero de elementos en un cluster
        positions = positions[0:max_size]
        for point in points:
            proj_point = []
            for idx,pos in enumerate(positions):
                pos = pos % self.dim
                proj_point.append(point[pos])
                positions[idx] = pos
            ret.append(tuple(proj_point))
        return (list(set(ret)),positions)


    @property
    def qhull(self):
        self._qhull = self._qhull or self.get_qhull(self.pv_array)
        return self._qhull

    @property
    def facets(self):
        self._facets =  self._facets or self.qhull.facets
        return self._facets

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

    def generate_pnml(self, filename=None):
        if not filename:
            # Tomo el archivo de entrada y le quito la extensión '.xes' si la tiene
            def_name = (self.filename.endswith('.xes') and self.filename[:-4])\
                    or self.filename or ''
            # Genero un nombre por default
            def_name = '%s-out.pnml'%(def_name)
            filename = def_name
        preamble = '<?xml version="1.0" encoding="UTF-8"?>\n'\
                   '<pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">\n'\
                   '  <net id="exit_net" type="http://www.pnml.org/version-2009/grammar/ptnet">\n'\
                   '    <name>\n'\
                   '      <text>"%s" Generater automagically with PacH</text>\n'\
                   '    </name>\n'\
                   '    <page id="page">\n'%(self.filename)
        places = '\n      <!-- Places -->\n'
        places_list = []
        for idx, place in enumerate(self.facets):
            # Contamos desde uno
            idx += 1
            place_id = "place-%04d"%idx
            place_name = ("%s"%(place)).replace('<=','&lt;=')
            places_list.append(
                    '      <place id="%s">\n'\
                    '        <name>\n'\
                    '          <text>%s</text>\n'\
                    '        </name>\n'\
                    '        <initialMarking>\n'\
                    '          <text>%d</text>\n'\
                    '        </initialMarking>\n'\
                    '      </place>'%(place_id,place_name,abs(place.offset)))
        places += '\n'.join(places_list)

        transitions = '\n      <!-- Transitions -->\n'
        transitions_list = []
        for idx in xrange(self.dim):
            # Contamos desde uno
            transition_id = 'trans-%04d'%(idx+1)
            transition_name = self.event_dictionary.get(idx,
                    'Transition %04d'%(idx+1))
            transitions_list.append(
                    '      <transition id="%s">\n'\
                    '        <name>\n'\
                    '          <text>%s</text>\n'\
                    '        </name>\n'\
                    '      </transition>\n'%(transition_id,transition_name))
        transitions += '\n'.join(transitions_list)

        arcs = '\n      <!-- Arcs -->\n'
        arcs_list = []
        seen_arcs = []
        for pl_id,place in enumerate(self.facets):
            # Contamos desde uno
            pl_id += 1
            place_id = 'place-%04d'%(pl_id)
            for tr_id, val in enumerate(place.normal):
                tr_id += 1
                # Si es cero no crear el arco
                if not val:
                    continue
                transition_id = 'trans-%04d'%(tr_id)
                if abs(val) != 1:
                    arc_value = '<inscription>'\
                            '<text>%s</text>'\
                            '</inscription>'%(abs(val))
                else:
                    arc_value = ''
                if val > 0:
                    arc_id = 'arc-P%04d-T%04d'%(pl_id,tr_id)
                    # El arco sale de un place y va hacia una transition
                    from_id = place_id
                    to_id = transition_id
                else:
                    arc_id = 'arc-T%04d-P%04d'%(tr_id,pl_id)
                    from_id = transition_id
                    to_id = place_id
                # Evitemos crear arcos repetidos crear arcos repetidos
                if (from_id, to_id) in seen_arcs:
                    continue
                else:
                    seen_arcs.append((from_id, to_id))
                arcs_list.append('      <arc id="%s" source="%s" target="%s">%s</arc>'
                                        %(arc_id,from_id,to_id,arc_value))
        arcs += '\n'.join(arcs_list)
        ending = '\n    </page>\n  </net>\n</pnml>\n'

        pnml = preamble + places + transitions + arcs + ending
        with open(filename,'w') as ffile:
            ffile.write(pnml)
        return True


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
            if not (filename.endswith('.xes') or filename.endswith('.txt')):
                print filename, ' does not end in .xes not .txt. It should...'
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
            proj_connected = False
            if '--projection' in sys.argv or '-p' in sys.argv:
                # None indicates not to do projection.
                # False indicates no limit
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
            filename = None
            if '--output' in sys.argv or '-o' in sys.argv:
                file_idx = '-o' in sys.argv and sys.argv.index('-o') or\
                    sys.argv.index('--output')
                try:
                    filename = sys.argv[file_idx+1]
                except:
                    pass
            pach.generate_pnml(filename=filename)
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

