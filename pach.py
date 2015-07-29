#!/usr/bin/env python
# -*- coding: UTF-8
from qhull import Qhull
from parser import XesParser
from utils import check_argv
import pdb
import time

class PacH(object):

    def __init__(self, filename, verbose=False):
        self.filename = filename
        self.parser = None
        self.qhull = None
        self.verbose = verbose

    def pach(self):
        start_time = time.time()
        self.parser = XesParser(self.filename)
        self.parser.parikhs_vector()
        if self.verbose:
            print 'Parikhs vector ready. Calculating MCH'
            elapsed_time = time.time() - start_time
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'
        self.qhull = Qhull(self.parser.points)
        ret = self.qhull.compute()
        elapsed_time = time.time() - start_time
        if self.verbose:
            print 'Finalizado el proceso'
            print '# RESULTADO  obtenido en: ', elapsed_time
            print '#'*40+'\n'
        print 'Diferent parsed points: {0}\n'\
            'Parsed points dimension: {1}\n'\
            'MCH points: {2}'.format(len(self.qhull.points),
                self.parser.dimension, ret)
        return ret


def main():
    usage = """
        Usage: ./pach <XES filename> [--debug][--verbose]
    """
    if not check_argv(sys.argv, minimum=1, maximum=4):
        print usage
        ret = -1
    else:
        ret = 0
        try:
            from os.path import isfile
            if '--debug' in sys.argv:
                pdb.set_trace()
            filename = sys.argv[1]
            if not filename.endswith('.xes'):
                print filename, ' does not end in .xes. It should...'
                raise Exception('Filename does not end in .xes')
            if not isfile(filename):
                raise Exception("El archivo especificado no existe")
            pach = PacH(filename, verbose=('--verbose' in sys.argv))
            pach.pach()
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

