#!/usr/bin/env python
# -*- coding: UTF-8
from halfspace import Halfspace
from custom_exceptions import IncorrectOutput, CannotGetHull
from qhull import Qhull
from config import logger

from itertools import izip
from z3 import (Solver,
    Int,
    Ints,
    Or,
    And,
    simplify,
    unsat,
    unknown
)

class SMTQhull(Qull):

    def __parse_smt_solution(self, model):
        """
         input: Output solution for Z3 Solver
         output: (dimension,nbr_facets,[halfspaces])
        """
        dim = len(self.points[0])

        facets = []
        try:
            facet_number = model[Int("FacetNumber")].as_long()
            for yaxis in xrange(facet_number):
                ti = Int('b%s' % yaxis)
                offset = model[ti].as_long()
                coeff = []
                for xaxis in xrange(dim):
                    coeff.append(model[Int('a%s,%s'%(yaxis,xaxis))])
                hs = Halfspace(coeff,offset)
                facets.append(hs)
        except Exception, err:
            logger.error('Incorrect output of smt-hull! Error: %s', err)
            raise IncorrectOutput()
        return (dim, facet_number, facets)



    def __smt_solution(self, equation_number):
        if len(self.points) < 1:
            logger.info('Cannot find solution for SMT-QULL with no points!')
            raise Exception('Cannot find solution for SMT-QULL with no points!')
        timeout = 3000 # TODO As argument?
        dim = len(list(points)[0])
        logger.info('Searching for hull in dimension %s based on %s points using SMT',
                dim,len(points))
        neg_points = self.neg_points or []

        """
        Ax+b<=0

        A \in mxn
        donde m es la cantidad a minimizar (i.e. la cantidad de ecuaciones)
        y n es igual a la dimensión en donde habitan los puntos

        Matrix's coefficients are represented as a#y,#x donde '#x' indica la columna e '#y' la fila
        """
        matrix = []
        evaluations = set()
        negatives = {}
        for yaxis in xrange(equation_nbr):
            # Define the list of coefficients for this equation
            coeff_list = Ints(' '.join('a%s,%s'%(yaxis,xaxis) for xaxis in xrange(dim)))
            # Define independent term for this equation
            ti = Int('b%s' % yaxis)
            # Build the matrix
            matrix.append(coeff_list + [ti])

            # Every point should be a solution of the system
            # i.e. it should we true that A[yaxis] * point + b[yaxis] >= 0
            for point in points:
                evaluation = ti
                for coeff, val in izip(coeff_list, point):
                    if val:
                        evaluation += coeff * val
                # Add to the "evaluation restriction set"
                evaluations.add(evaluation >= 0)
            # Every negative point should NOT be a solution of the system
            # i.e. it should we true that A[E] * npoint + b[E] < 0 for some E
            for npoint in neg_points:
                this_npoint_set = negatives.setdefault(npoint,set())
                evaluation = ti
                for coeff, nval in izip(coeff_list, npoint):
                    if nval:
                        evaluation += coeff * nval
                # Add to this point "negative restriction set"
                this_npoint_set.add(evaluation < 0)
        # Build the SMT problem
        solver = Solver()
        solver.set("zero_accuracy",10)
        solver.set("timeout", timeout)

        # All evaluations should be satisfied
        solver.add(And(list(evaluations)))
        for npoint, this_npoint_set in negatives.iteritems():
            solver.add(Or(list(this_npoint_set)))

        # Add facetnumber to the solver's solution for used when parsing output
        solver.add(Int("FacetNumber") == equation_nbr)

        sol = solver.check()
        if sol == unsat:
            ret = False
            logger.info('Z3 returns UNSAT: Cannot get hull without adding neg info')
        elif sol == unknown:
            ret = False
            logger.info('Z3 returns UNKNOWN: Cannot get hull in less than %s miliseconds', timeout)
        else:
            ret = solver.model()
        return ret

    def __smt_hull_bs(min_eq_nbr=1, max_eq_nbr=99):
        middle = (min_eq_nbr + max_eq_nbr) / 2
        sol = self.__smt_solution(middle)
        if min_eq_nbr == max_eq_nbr:
            ret = sol
        elif min_eq_nbr < middle:
            ret = self.__smt_qull_bs(min_eq_nbr=min_eq_nbr, max_eq_nbr=middle)
        elif sol:
            ret = sol
        elif max_eq_nbr > middle:
            ret = self.__smt_qull_bs(min_eq_nbr=middle, max_eq_nbr=max_midle)
        return ret

    @StopWatchObj.stopwatch
    def compute_hiperspaces(self):
        # Checks made in parent class
        super(Qull,self).compute_hiperspaces()

        model = self.__smt_hull_bs(min_eq_nbr=1, max_eq_nbr=99)
        try:
            dim, facets_nbr, facets = self.__parse_smt_solution(model)
        except IncorrectOutput, err:
            logger.error('Could not get hull')
            raise CannotGetHull()
        logger.info('Found hull in dimension %s of %s facets',
                dim,facets_nbr)
        self.dim = dim
        self.facets = facets
        return self.dim

if __name__ == '__main__':
    import sys, traceback,pdb
    from mains import qhull_main
    try:
        smt_qhull_main()
    except Exception, err:
        logger.error('SMT-Qhull Error: %s' % err, exc_info=True)
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        #pdb.post_mortem(tb)
