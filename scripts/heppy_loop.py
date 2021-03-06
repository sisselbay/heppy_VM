#!/usr/bin/env python
# Copyright (C) 2014 Colin Bernet
# https://github.com/cbernet/heppy/blob/master/LICENSE

import os
import shutil
import glob
import sys
import imp
import copy

from multiprocessing import Pool
from pprint import pprint

from heppy.framework.looper import Looper
from heppy.framework.config import split

# global, to be used interactively when only one component is processed.
loop = None

def callBack( result ):
    pass
    # print 'production done:', str(result)

def runLoopAsync(comp, outDir, config, options):
    loop = runLoop( comp, outDir, config, options)
    return loop.name

def runLoop( comp, outDir, config, options):
    fullName = '/'.join( [outDir, comp.name ] )
    # import pdb; pdb.set_trace()
    config.components = [comp]
    loop = Looper( fullName,
                   config,
                   options.nevents, 0,
                   nPrint = options.nprint,
                   timeReport = True,
                   quiet=options.quiet)
    # print loop
    if options.iEvent is None:
        loop.loop()
        loop.write()
        # print loop
    else:
        # loop.InitOutput()
        iEvent = int(options.iEvent)
        loop.process( iEvent )
    return loop

def createOutputDir(dirname, components, force):
    '''Creates the output dir, dealing with the case where dir exists.'''
    answer = None
    try:
        os.mkdir(dirname)
        return True
    except OSError:
        if not os.listdir(dirname):
            return True 
        else: 
            if force is True:
                return True
            else: 
                print 'directory %s already exists' % dirname
                print 'contents: '
                dirlist = [path for path in os.listdir(dirname) \
                               if os.path.isdir( '/'.join([dirname, path]) )]
                pprint( dirlist )
                print 'component list: '
                print [comp.name for comp in components]
                while answer not in ['Y','y','yes','N','n','no']:
                    answer = raw_input('Continue? [y/n]')
                if answer.lower().startswith('n'):
                    return False
                elif answer.lower().startswith('y'):
                    return True
                else:
                    raise ValueError( ' '.join(['answer can not have this value!',
                                                answer]) )
            

def main( options, args, parser):
    if len(args) != 2:
        parser.print_help()
        print 'ERROR: please provide the processing name and the component list'
        sys.exit(1)

    outDir = args[0]
    if os.path.exists(outDir) and not os.path.isdir( outDir ):
        parser.print_help()
        print 'ERROR: when it exists, first argument must be a directory.'
        sys.exit(2)
    cfgFileName = args[1]
    if not os.path.isfile( cfgFileName ):
        parser.print_help()
        print 'ERROR: second argument must be an existing file (your input cfg).'
        sys.exit(3)

    file = open( cfgFileName, 'r' )
    sys.path.append( os.path.dirname(cfgFileName) )
    cfg = imp.load_source( 'cfg', cfgFileName, file)

    selComps = [comp for comp in cfg.config.components if len(comp.files)>0]
    selComps = split(selComps)
    # for comp in selComps:
    #    print comp
    # if len(selComps)>14:
    #     raise ValueError('too many threads: {tnum}'.format(tnum=len(selComps)))
    if not createOutputDir(outDir, selComps, options.force):
        print 'exiting'
        sys.exit(0)
    if len(selComps)>1:
        shutil.copy( cfgFileName, outDir )
        pool = Pool(processes=len(selComps))
        for comp in selComps:
            pool.apply_async( runLoopAsync, [comp, outDir, cfg.config, options],
                              callback=callBack)
        pool.close()
        pool.join()
    else:
        # when running only one loop, do not use multiprocessor module.
        # then, the exceptions are visible -> use only one sample for testing
        global loop
        loop = runLoop( comp, outDir, cfg.config, options )


def create_parser(): 
    from optparse import OptionParser

    parser = OptionParser()
    parser.usage = """
    %prog <output_directory> <config_file>
    Start the processing of the jobs defined in your configuration file.
    """

    parser.add_option("-N", "--nevents",
                      dest="nevents",
                      help="number of events to process",
                      default=None)
    parser.add_option("-p", "--nprint",
                      dest="nprint",
                      help="number of events to print at the beginning",
                      default=5)
#COLIN TODO : interactive processing as in CMS
#    parser.add_option("-i", "--iEvent",
#                      dest="iEvent",
#                      help="jump to a given event. ignored in multiprocessing.",
#                      default=None)
    parser.add_option("-f", "--force",
                      dest="force",
                      action='store_true',
                      help="don't ask questions in case output directory already exists.",
                      default=False)
    parser.add_option("-q", "--quiet",
                      dest="quiet",
                      action='store_true',
                      help="do not print log messages to screen.",
                      default=False)
    return parser

if __name__ == '__main__':
    parser = create_parser()
    (options,args) = parser.parse_args()
    options.iEvent = None
    main(options, args, parser)
