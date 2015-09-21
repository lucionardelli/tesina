#!/usr/bin/env python
# -*- coding: UTF-8
import numpy as np
import random
from custom_exceptions import CannotGetClusters

def cluster_points(X, mu):
    clusters  = {}
    for x in X:
        bestmukey = min([(i[0], np.linalg.norm(x-mu[i[0]])) \
                    for i in enumerate(mu)], key=lambda t:t[1])[0]
        cluster = clusters.setdefault(bestmukey,[])
        cluster.append(x)
    return clusters

def reevaluate_centers(mu, clusters):
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        newmu.append(np.mean(clusters[k], axis = 0))
    return newmu

def has_converged(mu, oldmu):
    return set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu])

def find_centers(X, K, oldmu=None, mu=None):
    # X tiene que ser una lista de np.array
    # K es el número de clusters a generar
    # Initialize to K random centers
    if oldmu is None:
        oldmu = random.sample(X, K)
    if mu is None:
        mu = random.sample(X, K)
    while not has_converged(mu, oldmu):
        oldmu = mu
        # Assign all points in X to clusters
        clusters = cluster_points(X, mu)
        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)
    return(mu, clusters)

def two_means(points):
    # El algoritmo de kmeans espera un arreglo de NumPy arrays
    # El centroide inicial y el máximo hasta que CORR (o los eigenvectors en realidad)
    # esté bien. Luego puede usarse [0,1]
    clusters = cluster_points(points,[0,max(points)])
    if len(clusters) == 0:
        raise CannotGetClusters()
    return clusters.get(0,[]), clusters.get(1,[])
