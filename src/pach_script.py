#!/usr/bin/env python
# -*- coding: UTF-8
from os.path import isfile
import os, shutil

from pach import PacH
from config import logger
from utils import check_argv, parse_config, parse_config_output

def main(*args, **kwargs):
    usage = """
        Usage: ./pach_script.py <.ini config filename>
    """
    if not check_argv(sys.argv, minimum=1, maximum=4):
        print usage
        ret = -1
    else:
        ret = 0
        try:
            config_file = sys.argv[1]
            if not config_file.endswith('.ini'):
                print config_file, ' does not end in .ini. It should...'
                raise Exception('Filename has wrong extension')
            if not isfile(config_file):
                raise Exception("No such file")
            if '--debug' in sys.argv:
                pdb.set_trace()
            for filename, arguments in parse_config(config_file):
                pach = PacH(filename, **arguments)
                complexity = pach.pach()
                pach.generate_pnml()
                if '--verbose' in sys.argv:
                    print complexity
            pnml_folder,out_folder = parse_config_output(config_file)
            pwd= os.getcwd()
            for basename in os.listdir(pwd):
                if basename.endswith('.pnml'):
                    pnml_file = os.path.join(pwd, basename)
                    if os.path.isfile(pnml_file):
                        shutil.copy2(pnml_file, pnml_folder)
                        os.remove(pnml_file)
                elif basename.endswith('.out'):
                    out_file = os.path.join(pwd, basename)
                    if os.path.isfile(out_file):
                        shutil.copy2(out_file, out_folder)
                        os.remove(out_file)
        except Exception, err:
            ret = 1
            if hasattr(err, 'message'):
                print 'Error: ', err.message
            else:
                print 'Error: ', err
            logger.error('Error: %s' % err, exc_info=True)
            raise err
        return ret


if __name__ == '__main__':
    import sys, traceback, pdb
    try:
        main()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        #pdb.post_mortem(tb)

