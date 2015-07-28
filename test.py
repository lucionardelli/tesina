#!/usr/bin/env python
# -*- coding: UTF-8
from random import random
import time

DIMENSION = 9
POINTS = 1000

class Tester():
    def __init__(self, method=None, dim=DIMENSION, points=POINTS):
        self.method = method
        self.dim = dim
        self.points = points
        self.hiperspace = None


    def make_n_tuple(self):
        ret = []
        for x in xrange(self.dim):
            ret.append(random())
        return tuple(ret)

    def make_hiperspace(self):
        hiperspace = []
        for _ in xrange(self.points):
            hiperspace.append(self.make_n_tuple())
        self.hiperspace = hiperspace
        return self.hiperspace

    def run_test(self, dim=DIMENSION,points=POINTS):
        if self.hiperspace is None:
            self.make_hiperspace()
        start_time = time.time()
        ret = self.method(self.hiperspace)
        elapsed_time = time.time() - start_time
        print '#'*40+'\n'
        print '## RESULTADO  obtenido en: ', elapsed_time
        print '#'*40+'\n'
        print ret.vertices
        print '#'*40+'\n'
        print '## RESULTADO  obtenido en: ', elapsed_time
        print '#'*40+'\n'

def main():
    import sys, pdb
    usage = """
        Usage: ./test.py <module> <methodname> [--debug]
    """
    if (len(sys.argv) < 3 or len(sys.argv) > 4 or
        type(sys.argv[1]) != type('') or
        type(sys.argv[2]) != type('')):
        print usage
        return sys.exit(-1)
    else:
        exit = 0
        try:
            if '--debug' in sys.argv:
                pdb.set_trace()
            from importlib import import_module
            module_name = sys.argv[1]
            method_name = sys.argv[2]
            if '.py' in module_name:
                print module_name, 'assumed to be a file instead of module'
                module_name = module_name[0:module_name.find('.py')]
                print 'Using %s as "module" instead'%(module_name)
            module = import_module(module_name)
            if not hasattr(module, method_name):
                raise Exception('%s method not found in %s'%(method_name,module_name))

            method = getattr(module, method_name)
            tester = Tester(method)
            tester.run_test()
        except ImportError, err:
            exit = 1
            if hasattr(err, 'message'):
                print 'Import Error: ', err.message
            else:
                print 'Import Error: ', err
        except Exception, err:
            exit = 1
            if hasattr(err, 'message'):
                print 'Error: ', err.message
            else:
                print 'Error: ', err
        return sys.exit(exit)

if __name__ == '__main__':
    main()
