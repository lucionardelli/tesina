#!/usr/bin/env python
# -*- coding: UTF-8
from qhull import Qhull
from parser import XesParser, AdHocParser
from negative_parser import NegativeParser
from corrmatrix import CorrMatrix
from utils import get_positions, rotate_dict
import time
import numpy as np
from random import sample

from halfspace import Halfspace
from custom_exceptions import CannotGetHull, WrongDimension, CannotIntegerify
from sampling import sampling
from projection import projection

from config import logger
class PacH(object):

    def __init__(self, filename, verbose=False,
            samp_num=1, samp_size=None,
            proj_size=None, proj_connected=True,
            nfilename=None, max_coef=10,
            smt_matrix=False,
            smt_iter=False,
            smt_timeout=0,
            sanity_check=False):
        # El archivo de trazas
        logger.info('Positive traces file: %s', filename)
        self.filename = filename
        # El archivo de trazas negativas (if any)
        self.nfilename = nfilename
        logger.info('Negative traces file: %s', nfilename)
        self.verbose = verbose
        # Referentes a las trazas
        self.pv_traces = []
        self.pv_set = set()
        self.pv_array = np.array([])
        self._qhull = None
        # Referentes a las trazas negativas
        self.max_coef = max_coef
        self.npv_traces = []
        self.npv_set = set()
        self.npv_array = np.array([])
        # Inicialización de varibales
        self.dim = 0
        if smt_iter:
            logger.info('Will apply iterative SMT simplifications')
        self.smt_iter = smt_iter
        if smt_matrix:
            logger.info('Will apply SMT simplification')
        self.smt_matrix = smt_matrix
        self.smt_timeout = smt_timeout
        # Sampling configuration
        # At least we need one "sample"
        self.samp_num = max(samp_num,1)
        if self.samp_num > 1:
            logger.info('Will apply %s samples',self.samp_num)
        self.samp_size = samp_size
        if self.samp_size != 0:
            logger.info('Samples will have %s points',self.samp_size)
        # Projection configuration
        self.projections = {}
        # If proj_size is None, do not do projection
        if proj_size is not None:
            if proj_size:
                logger.info('Will apply projections of no more of %s points',
                        proj_size)
            else:
                logger.info('Will apply unbonded projections')
        self.proj_size = proj_size
        if proj_connected:
            logger.info('Will try to connect the projections')
        self.proj_connected = proj_connected
        # Do Sanity check after projectiong?
        self.sanity_check = sanity_check

    def parse_negatives(self):
        if not self.nfilename:
            logger.error('No se ha especificado un archivo '\
                    'de trazas negativas!')
            raise Exception('No se ha especificado un archivo '\
                    'de trazas negativas!')
        if self.verbose:
            print 'Starting parse of negative traces\n'
            start_time = time.time()
        if self.nfilename.endswith('.xes'):
            parser = NegativeParser(self.nfilename,
                    required_dimension=self.dim,
                    event_dictionary=self.event_dictionary)
        elif self.filename.endswith('.txt'):
           raise Exception('Not implemented yet!')
        else:
            logger.error("Error in file %s extension. Only '.xes'"\
                    " is allowed!",(self.nfilename or ''))
            raise Exception("Error in file %s extension. Only '.xes'"\
                    " is allowed!"%(self.nfilename or ''))
        parser.parikhs_vector()
        self.npv_traces = parser.pv_traces
        self.npv_set = parser.pv_set
        self.npv_array = parser.pv_array
        if self.verbose:
            print 'Parse of negative traces done\n'
            elapsed_time = time.time() - start_time
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'

    def parse_traces(self):
        if self.verbose:
            print 'Starting parse\n'
            start_time = time.time()
        if self.filename.endswith('.xes'):
            parser = XesParser(self.filename)
        elif self.filename.endswith('.txt'):
            parser = AdHocParser(self.filename)
        else:
            logger.error("Error in file %s extension. Only '.xes' and '.txt'"\
                    " are allowed!",(self.filename or ''))
            raise Exception("Error in file %s extension. Only '.xes' and '.txt'"\
                    " are allowed!"%(self.filename or ''))
        parser.parikhs_vector()
        self.event_dictionary = parser.event_dictionary
        self.reversed_dictionary = rotate_dict(parser.event_dictionary)
        self.pv_traces = parser.pv_traces
        self.pv_set = parser.pv_set
        self.pv_array = parser.pv_array
        self.dim = parser.dim
        if self.verbose:
            print 'Parse done\n'
            elapsed_time = time.time() - start_time
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'

    def parse(self):
        self.parse_traces()
        if self.nfilename:
            self.parse_negatives()

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
        proj_nbr = len(self.projections) + 1
        ret = set()
        # Por cada variable en el cluster
        # busco el valor correspondiente en los puntos iniciales
        # Los voy recorriendo en "orden de correlación"
        # El cluster viene dado por valores absolutos
        # pero por las dudas...
        cluster = list(set([abs(x) for x in cluster]))
        cluster.sort(reverse=True)
        proj_idx = []
        for proj in cluster:
            # Cuando conectamos dos proyecciones pasamos ambos valores concatenados
            proj_idx += [idx%self.dim for idx,val in enumerate(eigen) if abs(val) == proj\
                    and idx%self.dim not in proj_idx]

        for point in points:
            proj_point = list(np.array(point)[proj_idx])
            ret.add(tuple(proj_point))

        self.projections[proj_nbr] = proj_idx
        return (list(ret),proj_idx)

    @property
    def qhull(self):
        if not self._qhull:
            self._qhull = self.get_qhull(self.pv_array)
            self._qhull.prepare_negatives()
        return self._qhull

    @qhull.setter
    def qhull(self, qhull):
        self._qhull = qhull
        return self._qhull

    @property
    def facets(self):
        return self.qhull.facets

    @sampling
    @projection
    def get_qhull(self, points):
        points = set(map(tuple, points))
        qhull = Qhull(points, neg_points=list(self.npv_set))
        qhull.compute_hiperspaces()
        return qhull

    def remove_unnecesary(self):
        if self.nfilename:
            logger.debug('Starting to simplify model from negative points')
            if self.verbose:
                print 'Starting to simplify model from negative points\n'
                start_time = time.time()
            old_len = len(self.facets)
            self.qhull.simplify(max_coef=self.max_coef)
            removed = len(self.facets) - old_len
            if removed:
                logger.debug('We removed %d facets without allowing negative points',removed)
            else:
                logger.debug("Couldn't simplify model without adding negative points")
            if self.verbose:
                elapsed_time = time.time() - start_time
                print 'Ended simplify from negative points\n'
                print '# RESULTADO  obtenido en: ', elapsed_time
                if removed:
                    print 'We removed %d facets without allowing negative points' % removed
                else:
                    print "Couldn't simplify model without adding negative points"
                print '#'*40+'\n'

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
        logger.info("Ended with MCH with %s halfspaces",len(facets))
        if self.verbose:
            elapsed_time = time.time() - start_time
            print 'Modeling done\n'
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'

    def smt_simplify(self):
        if self.smt_matrix:
            self.qhull.smt_hull_simplify(timeout=self.smt_timeout)
        elif self.smt_iter:
            self.qhull.smt_facet_simplify(timeout=self.smt_timeout)

    @property
    def complexity(self):
        return self.qhull.complexity()

    def pach(self):
        logger.debug('Starting parsing')
        self.parse()
        logger.debug('Starting modeling')
        self.model()
        # Remove unnecesary facets wrt neg traces (if any)
        self.remove_unnecesary()
        # Remove unnecesary facets wrt neg traces
        # Apply smt_simplify.
        # Options are on the hull level, on every facet or none
        self.smt_simplify()
        return self.complexity

    def get_def_pnml_name(self):
        # Tomo el archivo de entrada y le quito la extensión '.xes' si la tiene
        def_name = (self.filename.endswith('.xes') and self.filename[:-4])\
                or self.filename or ''
        # Genero un nombre por default
        opts = ''
        if self.samp_num > 1:
            opts += '_s%d'%(self.samp_num)
            if self.samp_size:
                opts += '_%d'%(self.samp_size)
        if self.proj_size is not None:
            opts += '_p%d'%(self.proj_size)
        def_name = '%s.pnml'%(def_name+opts)
        return def_name

    def generate_pnml(self, filename=None):
        if not filename:
            filename = self.get_def_pnml_name()
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
        for idx, place in enumerate(self.facets,1):
            nbr_places += 1
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
            if idx in self.reversed_dictionary:
                transition_id = self.reversed_dictionary.get(idx).replace(' ','_')
                transition_name = self.reversed_dictionary.get(idx)
            else:
                transition_id = 'trans-%04d'%(idx+1)
                transition_name = 'Transition %04d'%(idx+1)
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
        needs_preset = set(range(self.dim))
        needs_postset = set(range(self.dim))

        arcs_list = []
        seen_arcs = []
        for pl_id,place in enumerate(self.facets,1):
            # Contamos desde uno
            place_id = 'place-%04d'%(pl_id)
            for tr_id, val in enumerate(place.normal):
                # Si es cero no crear el arco
                if not val:
                    continue

                if tr_id in self.reversed_dictionary:
                    transition_id = self.reversed_dictionary.get(tr_id).replace(' ','_')
                else:
                    transition_id = 'trans-%04d'%(tr_id+1)
                if abs(val) != 1:
                    arc_value = '<inscription>'\
                            '<text>%s</text>'\
                            '</inscription>'%(abs(val))
                else:
                    arc_value = ''
                if val > 0:
                    if tr_id in needs_preset:
                        # Puede que ya le hayamos creado un arco
                        # entrante
                        needs_preset.remove(tr_id)
                    arc_id = 'arc-P%04d-T%s'%(pl_id,transition_id)
                    # El arco sale de un place y va hacia una transition
                    from_id = place_id
                    to_id = transition_id
                else:
                    if tr_id in needs_postset:
                        # Puede que ya le hayamos creado un arco
                        # saliente
                        needs_postset.remove(tr_id)
                    arc_id = 'arc-T%s-P%04d'%(transition_id,pl_id)
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
            else:
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


            if tr_id in self.reversed_dictionary:
                transition_id = self.reversed_dictionary.get(tr_id).replace(' ','_')
            else:
                transition_id = 'trans-%04d'%(tr_id)
            if tr_id in needs_preset:
                # Si necesita preset, nos indica que la transición se puede
                # disparar siempre, por lo que generamos un loop
                # con el dummy-place
                arc_id = 'arc-P%04d-T%s'%(pl_id,transition_id)
                loops_list.append('      <arc id="%s" source="%s" target="%s">%s</arc>'
                                                %(arc_id,transition_id,place_id,1))
                arc_id = 'arc-T%s-P%04d'%(tr_id,pl_id)
                loops_list.append('      <arc id="%s" source="%s" target="%s">%s</arc>'
                                                %(arc_id,place_id,transition_id,1))
            elif tr_id in needs_postset:
                # Lo agregamos al postset de la transición como una
                # especie de "/dev/null" donde tirar los markings generados
                arc_id = 'arc-T%s-P%04d'%(tr_id,pl_id)
                loops_list.append('      <arc id="%s" source="%s" target="%s">%s</arc>'
                                                %(arc_id,transition_id,place_id,1))
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
        logger.info('Generated the PNML %s', filename)
        return True

if __name__ == '__main__':
    import sys, traceback, pdb
    from mains import pach_main
    try:
        pach_main()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        #pdb.post_mortem(tb)


