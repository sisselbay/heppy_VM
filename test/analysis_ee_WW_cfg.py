'''Example configuration file for an ee->WW->had+lep analysis in heppy, with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from analysis_ee_WW_cfg import * 
'''

import os
import copy
import heppy.framework.config as cfg

from heppy.framework.event import Event
Event.print_patterns=['*jet*', 'sum*']

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

# setting the random seed for reproducible results
import heppy.statistics.rrandom as random
random.seed(0xdeadbeef)

# definition of the collider
from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 240.

# input definition
comp = cfg.Component(
    'ee_WW_hadLep',
    files = [
        'ee_WW_hadLep.root'
    ]
)
selectedComponents = [comp]



# read FCC EDM events from the input root file(s)
# do help(Reader) for more information
from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

from heppy.analyzers.P4SumBuilder import P4SumBuilder
sum_particles = cfg.Analyzer(
    P4SumBuilder, 
    output='sum_all_ptcs',
    #    particles='gen_particles_stable'
    particles='rec_particles'
)

sum_gen = cfg.Analyzer(
    P4SumBuilder, 
    output='sum_all_gen',
    particles='gen_particles_stable'
)


#######################################################
# From Workdir/analysis_ee_ZH_cfg.py 

# Use a Filter to select leptons from the output of papas.
# Currently, we're treating electrons and muons transparently.
# we could use two different instances for the Filter module
# to get separate collections of electrons and muons
# help(Filter) for more information
from heppy.analyzers.Filter import Filter
leptons_true = cfg.Analyzer(
    Filter,
    'sel_leptons',
    output = 'leptons_true',
    # output = 'leptons',
    input_objects = 'gen_particles',
    filter_func = lambda ptc: ptc.e()>10. and abs(ptc.pdgid()) in [11, 13]
)

# Make jets from the particles not used to build the best zed.
# Here the event is forced into 2 jets to target ZH, H->b bbar)
# help(JetClusterizer) for more information
from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jet',
    particles = 'gen_particles',
    fastjet_args = dict( njets = 2)  
)

########################################################
# Building Ws
# help(ResonanceBuilder) for more information
from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
Ws = cfg.Analyzer(
    ResonanceBuilder,
    output = 'Ws',
    leg_collection = 'leptons_true',
    pdgid = 24
)
########################################################

# Analysis-specific ntuple producer
# please have a look at the WWTreeProducer class
from heppy.analyzers.WWTreeProducer import WWTreeProducer
WW_tree = cfg.Analyzer(
    WWTreeProducer,
    leptons = 'leptons_true',
    jets = 'jets',
    Ws = 'Ws'
#    zeds = 'zeds',
#    jets = 'jets'
   # higgses = 'higgses',
   # recoil  = 'recoil'
)
########################################################

# Here I need to builds WW's
# use lepton builder
# count mu
# build jets
# only accep 1 mu   check in code "not zeds"
# make recoil -> nu



from heppy.analyzers.GlobalEventTreeProducer import GlobalEventTreeProducer
zed_tree = cfg.Analyzer(
    GlobalEventTreeProducer, 
    sum_all='sum_all_ptcs', 
    sum_all_gen='sum_all_gen',
)


from heppy.test.papas_cfg import gen_particles_stable, papas_sequence, detector, papas
from heppy.test.jet_tree_cff import jet_tree_sequence


# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    # gen_particles_stable, 
    papas_sequence,
    jet_tree_sequence('gen_particles_stable',
                      'rec_particles',
                      2, None),
    sum_particles,
    sum_gen, 
    leptons_true,  #
#    jets,  #
#    Ws,
    zed_tree,
    WW_tree  #
    )

# Specifics to read FCC events 
from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    import heppy.statistics.rrandom as random
    random.seed(0xdeadbeef)

    def process(iev=None):
        if iev is None:
            iev = loop.iEvent
        loop.process(iev)
        if display:
            display.draw()

    def next():
        loop.process(loop.iEvent+1)
        if display:
            display.draw()            

    iev = None
    usage = '''usage: python analysis_ee_ZH_cfg.py [ievent]
    
    Provide ievent as an integer, or loop on the first events.
    You can also use this configuration file in this way: 
    
    heppy_loop.py OutDir/ analysis_ee_ZH_cfg.py -f -N 100 
    '''
    if len(sys.argv)==2:
        papas.display = True
        try:
            iev = int(sys.argv[1])
        except ValueError:
            print usage
            sys.exit(1)
    elif len(sys.argv)>2: 
        print usage
        sys.exit(1)
            
        
    loop = Looper( 'looper', config,
                   nEvents=10,
                   nPrint=5,
                   timeReport=True)
    
    simulation = None
    for ana in loop.analyzers: 
        if hasattr(ana, 'display'):
            simulation = ana
    display = getattr(simulation, 'display', None)
    simulator = getattr(simulation, 'simulator', None)
    if simulator: 
        detector = simulator.detector
    if iev is not None:
        process(iev)
    else:
        loop.loop()
        loop.write()
