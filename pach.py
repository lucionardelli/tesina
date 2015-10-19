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
from sampling import sampling
from projection import projection

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
        # The actual work is done when accesing self.facets
        facets = self.facets
        if self.verbose:
            print "Ended with MCH with ",len(facets)," halfspaces"
            print 'This are them:\n'
            for facet in facets:print facet
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

        # Comenzamos con los Places (i.e. un place por cada inecuación)
        nbr_places = 0
        places = '\n      <!-- Places -->\n'
        places_list = []
        for idx, place in enumerate(self.facets):
            nbr_places += 1
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

        # Seguimos con las Transitions (i.e. una transition por cada variable)
        # Se crearán tantas transiciones como dimensiones del espacio
        nbr_transitions = 0
        transitions = '\n      <!-- Transitions -->\n'
        transitions_list = []
        for idx in xrange(self.dim):
            nbr_transitions += 1
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

        # Los arcos se arman relacionando los places con las transitions
        # Para cada inecuación, se crean un arco hacia la transition
        # (i.e. variable) con peso igual al TI que la acompaña
        # Salvo que sea 0, claro.
        arcs = '\n      <!-- Arcs -->\n'

        # Para las transiciones que no tienen
        # al menos un elemento en el preset y uno en el postset
        # (i.e un arco que venga de una place y otra que salga hacia otro place)
        # le creamos un place ficticio para ponerlo en su pre y/o post
        needs_preset = set(range(1,self.dim+1))
        needs_postset = set(range(1,self.dim+1))

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
                    if pl_id in needs_preset:
                        # Puede que ya le hayamos creado un arco
                        # entrante
                        needs_preset.remove(pl_id)
                    arc_id = 'arc-P%04d-T%04d'%(pl_id,tr_id)
                    # El arco sale de un place y va hacia una transition
                    from_id = place_id
                    to_id = transition_id
                else:
                    if pl_id in needs_postset:
                        # Puede que ya le hayamos creado un arco
                        # saliente
                        needs_postset.remove(pl_id)
                    arc_id = 'arc-T%04d-P%04d'%(tr_id,pl_id)
                    from_id = transition_id
                    to_id = place_id
                # No debería pasar, pero por las dudas,
                # evitemos crear arcos repetidos
                if (from_id, to_id) in seen_arcs:
                    print 'El arco está repetido!: ', from_id, to_id
                    continue
                else:
                    seen_arcs.append((from_id, to_id))
                arcs_list.append('      <arc id="%s" source="%s" target="%s">%s</arc>'
                                        %(arc_id,from_id,to_id,arc_value))

        arcs += '\n'.join(arcs_list)

        # Generamos los places y arcos para los bucles de las transitions
        # desconectadas
        loops_list = []
        for idx,tr_id in enumerate(needs_preset | needs_postset):
            pl_id = nbr_places + idx + 1
            place_id = "place-%04d"%(pl_id)
            place_name = 'Dummy place %04d'%(idx+1)

            if tr_id in needs_preset:
                place_value = 1
            elif tr_id in needs_postset:
                place_value = 0
            else
                raise Exception('No necesita pre ni post!')

            loops_list.append(
                    '      <place id="%s">\n'\
                    '        <name>\n'\
                    '          <text>%s</text>\n'\
                    '        </name>\n'\
                    '        <initialMarking>\n'\
                    '          <text>%d</text>\n'\
                    '        </initialMarking>\n'\
                    '      </place>'%(place_id,place_name,place_value))

            transition_id = 'trans-%04d'%(tr_id)
            if tr_id in needs_preset:
                # Si necesita preset, nos indica que la transición se puede
                # disparar siempre, por lo que generamos un loop
                # con el dummy-place
                arc_id = 'arc-P%04d-T%04d'%(pl_id,tr_id)
                loops_list.append('      <arc id="%s" source="%s" target="%s">%s</arc>'
                                                %(arc_id,transition_id,place_id,1))
                arc_id = 'arc-T%04d-P%04d'%(tr_id,pl_id)
                loops_list.append('      <arc id="%s" source="%s" target="%s">%s</arc>'
            elif tr_id in needs_postset:
                # Lo agregamos al postset de la transición como una
                # especie de "/dev/null" donde tirar los markings generados
                arc_id = 'arc-T%04d-P%04d'%(tr_id,pl_id)
                loops_list.append('      <arc id="%s" source="%s" target="%s">%s</arc>'
                                                %(arc_id,place_id,transition_id,1))
        if len(loops_list) == 0:
            loops = ''
        else:
            loops = '\n      <!-- Dummy Places -->\n'
            loops += '\n'.join(loops_list)

        # Finalizamos el archivo
        ending = '\n    </page>\n  </net>\n</pnml>\n'

        pnml = preamble + places + transitions + arcs + loops + ending
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

