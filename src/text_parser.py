#!/usr/bin/env python
# -*- coding: UTF-8
from os.path import isfile
from lxml import etree
import pdb
import numpy as np

from config import logger

from generic_parser import GenericParser

class AdHocParser(GenericParser):
    def _parse(self):
        """
            parse txt file given as argument,
            returning a dict of trace (as list of char), and the lenght of it
                the maximum lenght in between all traces
                the (first) trace where this maximum is reached
        """
        with open(self.filename,'r') as ffile:
            # Iterate over traces
            for idx, trace in enumerate(ffile.readlines()):
                # Iterate over the events of the given trace
                trace = trace.replace('  ',' ')
                trace = trace.strip()
                trace = trace.replace('\n','')
                for event_idx, value in enumerate(trace.split(' ')):
                    # Search the list of points for current trace
                    tr_val = self.traces.setdefault(idx,{'trace': [], 'length': 0,})
                    if value not in self.event_dictionary:
                        self.event_dictionary[value] = len(self.event_dictionary)
                    tr_val['trace'].append(value)
                    tr_val['length'] += 1
        self.dim = len(self.event_dictionary)
        return True


if __name__ == '__main__':
    import sys, traceback
    from mains import parser_main
    try:
        parser_main()
    except Exception, err:
        logger.error('Error: %s' % err, exc_info=True)
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        #pdb.post_mortem(tb)

