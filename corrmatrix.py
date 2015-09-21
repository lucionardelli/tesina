#!/usr/bin/env python
# -*- coding: UTF-8
import numpy as np
class CorrMatrix(object):
    """
    """

    def __init__(self, pv_array, verbose=False):
        # Verbose
        self.verbose = verbose
        # Standard deviation
        self.std_dev = pv_array.std(axis=0)
        # Mean deviation
        self.mean_dev = pv_array.mean(axis=0)
        # This function actually computes everything
        self._make_corr_matrix(pv_array)
        if self.verbose:
            print 'La matriz de CORRelación entontrada es: '
            print self.matrix
            print 'Los eigenvalues de la matriz son: '
            print self.eigenvalues
            print 'Los eigenvectors de la matriz son: '
            print self.eigenvector

    def _make_corr_matrix(self, pv_array):
        """
            make Correlation Matrix for all pair of events
        """
        dim = len(pv_array) > 0 and len(pv_array[0]) or 0
        self.dim = dim
        matrix = np.zeros((dim,dim))
        aux = np.add(pv_array,-1 * self.mean_dev).T
        len_m1 = len(pv_array) -1
        for x_axis in xrange(dim):
            for y_axis in xrange(dim):
                numerador = aux[x_axis].dot(aux[y_axis])
                denominador = len_m1 * self.std_dev[x_axis] *\
                        self.std_dev[y_axis]
                if denominador == 0:
                    matrix[x_axis][y_axis] = 0
                else:
                    matrix[x_axis][y_axis] = np.divide(numerador,denominador)
        self.matrix = matrix
        self.eigenvalues, self.eigenvector = np.linalg.eig(matrix)
        return True

    def update(self, row_idx, make_zero):
        row = self.matrix[row_idx]
        for x in xrange(self.dim):
            if row[x] in make_zero:
                self.matrix[:,x] = np.zeros(self.dim)
        self.eigenvalues, self.eigenvector = np.linalg.eig(self.matrix)
