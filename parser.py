#!/usr/bin/env python
# -*- coding: UTF-8
from os.path import isfile
import sys
from lxml import etree
from utils import add_to_position
import pdb

class XesParser(object):
    def __init__(self,xes_file_name):
        if not isfile(xes_file_name):
            raise Exception("El archivo especificado no existe")
        self.filename = xes_file_name
        self.pv_list = {}
        self.points = set()
        self.root = None
        self.traces = {}
        self.max_len = 0
        self.max_len_idx = None
        self.event_pos = {}

    def initialize(self):
        self._parse()
        self._make_parikhs_vector()
        return True

    def _parse(self):
        """
            parse xes file given as argument,
            returning a dict of trace (as list of char), and the lenght of it
                the maximum lenght in between all traces
                the (first) trace where this maximum is reached
        """
        tree = etree.parse(self.filename)
        self.root = tree.getroot()
        seen_events = 0
        for idx, trace in enumerate(self.root.iterchildren(tag='{http://www.xes-'\
                'standard.org/}trace')):
            for event_idx, event in enumerate(trace.iterchildren(tag='{http://www.xes-standard.org/}event')):
                values = [x.get('value') for x in\
                    event.iterchildren(tag='{http://www.xes-standard.org/}string')\
                    if x.get('key') == "concept:name"]
                assert len(values) == 1, "No se puede obetner el  valor para el "\
                        "evento {0} de la traza {1}".format(event_idx, idx)
                value = values[0]
                if value not in self.event_pos:
                    self.event_pos[value] = seen_events
                    seen_events += 1
                tr_val = self.traces.setdefault(idx,{'trace': [], 'length': 0,})
                tr_val['trace'].append(value)
                tr_val['length'] += 1
                if tr_val['length'] > self.max_len:
                    self.max_len = tr_val['length']
                    self.max_len_idx = idx
        return True

    def _make_parikhs_vector(self):
        """
            make parickhs vector of all traces
        """
        null_point = [0]*self.max_len
        for idx,trace in self.traces.items():
            this_pv_list = self.pv_list.setdefault(idx,[null_point])
            for val in trace['trace']:
                # No hay valor por defecto, debería estar siempre en el dict
                pos = self.event_pos.get(val)
                last_pv = add_to_position(this_pv_list[-1], pos, value=1)
                self.points.add(tuple(last_pv))
                this_pv_list.append(last_pv)
        return True



def main():
    import sys
    usage = """
        Usage: ./parser.py <XES filename> [--verbose][--debug]
    """
    if (len(sys.argv) < 2 or len(sys.argv) > 4 or
        type(sys.argv[1]) != type('') or
        type(sys.argv[2]) != type('')):
        print usage
        return sys.exit(-1)
    else:
        exit = 0
        try:
            if '--debug' in sys.argv:
                pdb.set_trace()
            filename = sys.argv[1]
            if not filename.endswith('.xes'):
                print filename, 'does not end in .xes. It should...'
            if not isfile(filename):
                raise Exception("El archivo especificado no existe")
        except Exception, err:
            exit = 1
            if hasattr(err, 'message'):
                print 'Error: ', err.message
            else:
                print 'Error: ', err
        obj = XesParser('/tmp/a22.xes')
        obj.initialize()
        if '--verbose' in sys.argv:
            for trace in obj.pv_list:
                print 'Traza {0} with points:'.format(trace)
                for point in obj.pv_list[trace]:
                    print(point)
        print "#"*15
        print 'Se encontraron {0} puntos en un espacio de dimensión {1}'.format(
                len(obj.points), obj.max_len)
        print "#"*15
        return sys.exit(exit)

if __name__ == '__main__':
    main()

