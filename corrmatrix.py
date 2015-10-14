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
        if pv_array is not None:
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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.matrix.__str__()

    def __getitem__(self, idx):
        return self.matrix[idx]

    def copy(self):
        matrix = CorrMatrix(None,verbose=self.verbose)
        matrix.std_dev = self.std_dev.copy()
        matrix.mean_dev = self.mean_dev.copy()
        matrix.dim = self.dim
        matrix.matrix = self.matrix.copy()
        matrix.eigenvalues =  self.eigenvalues.copy()
        matrix.eigenvector = self.eigenvector.copy()
        return matrix

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

    def closest_points(self,clusters):
        rel = {}
        closest_tuple = (None,None)
        max_all = 0
        for key,cluster in clusters.items():
            for point in cluster:
                corr_list = rel.setdefault(point,[])
                for idx,corr in enumerate(self[point,:]):
                    corr = abs(corr)
                    if idx in cluster:
                        corr_list.append(0)
                        continue
                    corr_list.append(corr)
                    if max_all < corr:
                        closest = idx
                        max_all = corr
                        closest_tuple = (point,idx)

        p0,p1 = closest_tuple
        cor0 = np.array(rel[p0])
        cor1 = np.array(rel[p1])
        return  p0,p1,cor0,cor1

    def closest_point(self,cluster):
        rel = {}
        closest_tuple = (None,None)
        max_all = 0
        for point in cluster:
            corr_list = rel.setdefault(point,[])
            for idx in xrange(self.dim):
                if idx in cluster:
                    corr_list.append(0)
                    continue
                else:
                    corr = abs(self[point][idx])
                    corr_list.append(corr)
                    if max_all < corr:
                        max_all = corr
                        closest = idx
                        p0,p1 = (point,idx)
        cor0 = self[p0]
        cor1 = self[p1]
        return  p0,p1,cor0,cor1
