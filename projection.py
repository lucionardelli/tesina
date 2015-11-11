#!/usr/bin/env python
# -*- coding: UTF-8
import numpy as np
from corrmatrix import CorrMatrix
from kmeans import two_means

from config import *

def projection(func):
    def do_projection(self, points, *args, **kwargs):
        # Calculamos la matrix de correlaciones
        points = np.array(list(points))
        if self.proj_size is None:
            # Si el máximo es None es porque no se desea hacer projection
            logger.debug('Calculate hull without projection')
            qhull = func(self, points, *args, **kwargs)
        else:
            # Hacemos projection
            corr = CorrMatrix(points)
            corr2 = corr.copy()
            facets = []
            qhull = None
            projections = {}
            proj_count = 0
            logger.debug('Calculate hull with projection')
            while True:
                proj_count += 1
                logger.debug('Projection #%s',proj_count)
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
                logger.debug('Leader row # of CORR matrix %s',idx)
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
                        logger.error("We couldn't  get even a single cluster!")
                        # Aunque la proyección sea mala,
                        # tenemos que hacer al menos una.
                        cluster0,cluster1 = two_means(leader_row)
                        while len(cluster1) <= 1:
                            cluster1.append(max(cluster0))
                        logger.error('Using %s as the cluster closer to 1',cluster1)
                pts_proj, projected = self.project(points, leader_row, cluster1)
                logger.info('We will project onto this points: %s', projected)
                projections[proj_count] = projected
                qhull = func(self, pts_proj, *args, **kwargs)
                # Extendemos a la dimensión original
                qhull.extend(leader_row, cluster1)
                # Agregamos las facetas que ya calculamos
                qhull.union(facets)
                facets = qhull.facets

                #NOTE
                # Esto es para chequear que no dejando a nadia afuera
                # pero hace todo más lento en ejemplos grandes
                #where = qhull.separate(self.pv_set)
                #if len(where.get('outside',[])) > 0:
                #    log.error('Nooo!!!! We lost somebody!')
                #    import pdb;pdb.set_trace()
                #    qhull.separate(where['outside'])

                # Actualizamos la matriz poniendo en 0 los valores usados
                corr.update(projected)
            if self.proj_connected:
                # Intentamos hacer que el modelo sea conexo
                # con este algoritmo heurístico
                logger.info('Connecting projections')
                last_con_line = None
                connections_count = 0
                while True:
                    try:
                        p0,p1,cor0,cor1 = corr2.closest_points(projections)
                        logger.debug('Closer points are %s and %s', p0, p1)
                        if not (np.any(cor0) and np.any(cor1)):
                            break
                        con_line = cor0 + cor1
                        if np.any(last_con_line) and np.all(last_con_line==con_line):
                            break
                        else:
                            last_con_line = con_line
                        _, cluster1 = two_means(con_line,max_size=self.proj_size)
                        if len(cluster1) <= 1:
                            break
                        pts_proj, projected = self.project(points, con_line, cluster1)
                        qhull = func(self, pts_proj, *args, **kwargs)
                        # Extendemos a la dimensión original
                        qhull.extend(con_line, cluster1)
                        # Agregamos las facetas que ya calculamos
                        qhull.union(facets)
                        facets = qhull.facets
                        # Actualizamos la matriz poniendo en 0 los valores usados
                        corr2.update(projected)
                        connections_count += 1
                    except Exception, err:
                        pass
                    logger.info('Succesfull connections of projections: %s',connections_count)
        return qhull
    return do_projection

