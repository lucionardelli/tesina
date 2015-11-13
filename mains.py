#!/usr/bin/env python
# -*- coding: UTF-8
from utils import check_argv, get_positions
import pdb
import sys
from os.path import isfile
from pach import PacH
from qhull import Qhull
from parser import XesParser, AdHocParser
from negative_parser import NegativeParser

def pach_main():
    usage = 'Usage: ./pach <LOG filename> [--debug][--verbose]'\
        '\n\t[--negative <Negative points filename>] ]'\
        '\n\t[--sampling [<number of samplings>] [<sampling size>]]'\
        '\n\t[--projection [<max group size>] [<connected model>]]'\
        '\n\t[--smt-matrix [<timeout>]]'\
        '\n\t[--smt-iter [<timeout>]]'\
        '\n\t[--no-sanity]'
    if not check_argv(sys.argv, minimum=1, maximum=16):
        print usage
        ret = -1
    else:
        ret = 0
        try:
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
            proj_connected = True
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
            nfilename = None
            if '--negative' in sys.argv or '-n' in sys.argv:
                nidx = '-n' in sys.argv and sys.argv.index('-n') or\
                    sys.argv.index('--negative')
                nfilename = sys.argv[nidx+1]
                if not (nfilename.endswith('.xes') or nfilename.endswith('.txt')):
                    print nfilename, ' does not end in .xes not .txt. It should...'
                    raise Exception('Filename does not end in .xes')
                if not isfile(nfilename):
                    raise Exception("El archivo especificado no existe")

            smt_matrix = False
            smt_iter = False
            smt_timeout = 0
            if '--smt-matrix' in sys.argv or '-smt-m' in sys.argv:
                smt_idx = '-smt-m' in sys.argv and sys.argv.index('-smt-m') or\
                    sys.argv.index('--smt-matrix')
                smt_matrix = True
                try:
                    smt_timeout = int(sys.argv[smt_idx+1])
                except:
                    pass
            elif '--smt-iter' in sys.argv or '-smt-i' in sys.argv:
                smt_idx = '-smt-i' in sys.argv and sys.argv.index('-smt-i') or\
                    sys.argv.index('--smt-iter')
                smt_iter = True
                try:
                    smt_timeout = int(sys.argv[smt_idx+1])
                except:
                    pass
            sc = True
            if '--no-sanity' in sys.argv:
                sc = False
            if '--debug' in sys.argv:
                pdb.set_trace()
            pach = PacH(filename, verbose=('--verbose' in sys.argv),
                    samp_num=samp_num, samp_size=samp_size,
                    proj_size=proj_size, proj_connected=proj_connected,
                    nfilename=nfilename,
                    smt_matrix=smt_matrix,
                    smt_iter=smt_iter,
                    smt_timeout=smt_timeout,
                    sanity_check=sc)
            complexity = pach.pach()
            print '%s\t\t -> %s'%(filename,complexity)
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
            raise err
        return ret

def parser_main():
    usage = """
        Usage: ./parser.py <LOG filename> [--verbose][--debug]
    """
    if not check_argv(sys.argv, minimum=1, maximum=4):
        print usage
        ret = -1
    else:
        ret = 0
        try:
            if '--debug' in sys.argv:
                pdb.set_trace()
            filename = sys.argv[1]
            if not (filename.endswith('.xes') or filename.endswith('.txt')):
                print filename, ' does not end in .xes nor .txt. It should...'
                raise Exception('Filename has wrong extension')
            if not isfile(filename):
                raise Exception("El archivo especificado no existe")
            if filename.endswith('.xes'):
                obj = XesParser(filename, verbose='--verbose' in sys.argv)
            elif filename.endswith('.txt'):
                obj = AdHocParser(filename, verbose='--verbose' in sys.argv)
            obj.parse()
            if '--verbose' in sys.argv:
                print 'Parse done. Calcuting Parikhs vector'
            obj.parikhs_vector()
            CorrMatrix(obj.pv_array)
            print 'Se encontraron {0} puntos en un espacio de dimensión {1}'.format(
                    len(obj.pv_set), obj.dim)
            if '--verbose' in sys.argv:
                print "#"*15
        except Exception, err:
            ret = 1
            if hasattr(err, 'message'):
                print 'Error: ', err.message
            else:
                print 'Error: ', err
            raise err
        return ret

def qhull_main():
    usage = 'Usage: ./qhull <points> [--debug][--verbose]'
    if not check_argv(sys.argv, minimum=1, maximum=5):
        print usage
        ret =  -1
    else:
        ret = 0
        try:
            import ast
            try:
                if isfile(sys.argv[1]):
                    print sys.argv[1], 'assumed to be a file'
                    with open(sys.argv[1], 'r') as ffile:
                            points = ffile.readline()
                else:
                    points = sys.argv[1]
                points = ast.literal_eval(points)
                if '--verbose' in sys.argv:
                    print "Se colectaron ", len(points), " puntos"
                points = set(map(lambda x: tuple(x),points))
                if '--verbose' in sys.argv:
                    print "Se colectaron ", len(points), " puntos DIFERENTES"
            except:
                ret = -1
                print "We are sorry. We weren't able to read the points"
            else:
                if '--debug' in sys.argv:
                    pdb.set_trace()
                qhull = Qhull(points, verbose='--verbose' in sys.argv)
                point_qty = qhull.compute()
                print "Computed MCH with ", point_qty," points"
                if '--verbose' in sys.argv:
                    print 'This are the points:'
                    print(qhull.vertices)
        except Exception, err:
            ret = 1
            if hasattr(err, 'message'):
                print 'Error: ', err.message
            else:
                print 'Error: ', err
            raise err
    return ret

def negative_parser_main():
    usage = """
        Usage: ./parser.py <negative XES LOG filename> [--verbose][--debug]
    """
    if not check_argv(sys.argv, minimum=1, maximum=4):
        print usage
        ret = -1
    else:
        ret = 0
        try:
            filename = sys.argv[1]
            if not filename.endswith('.xes'):
                print filename, ' does not end in .xes. It should...'
                raise Exception('Filename has wrong extension')
            if not isfile(filename):
                raise Exception("El archivo especificado no existe")
            if '--debug' in sys.argv:
                pdb.set_trace()
            obj = NegativeParser(filename, verbose='--verbose' in sys.argv)
            obj.parse()
            if '--verbose' in sys.argv:
                print 'Parse done. Calcuting Parikhs vector'
            obj.parikhs_vector()
            print 'Se encontraron {0} puntos en un espacio de dimensión {1}'.format(
                    len(obj.pv_set), obj.dim)
            if '--verbose' in sys.argv:
                print "#"*15
        except Exception, err:
            ret = 1
            if hasattr(err, 'message'):
                print 'Error: ', err.message
            else:
                print 'Error: ', err
            raise err
        return ret

