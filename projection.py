#!/usr/bin/env python
# -*- coding: UTF-8
import numpy as np
from corrmatrix import CorrMatrix
from kmeans import two_means

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

