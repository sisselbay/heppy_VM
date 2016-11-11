import os
import copy
import heppy.framework.config as cfg

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

comp = cfg.Component(
    'example',
    files = ['ee_ZH_Z_Hbb.root'] #  ZH_Zmumu_Hgg.root']
)
selectedComponents = [comp]

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader
)

from heppy.analyzers.LeptonAnalyzer import LeptonAnalyzer
papas_muons = cfg.Analyzer(
    LeptonAnalyzer,
    instance_label = 'papas_muons',
    particles = 'papas_rec_particles',
    pdgid = 13
)

from heppy.analyzers.ParticlesForJets import ParticlesForJets
rec_particles_for_jets = cfg.Analyzer(
    ParticlesForJets,
    'rec_particles_for_jets',
    particles = 'papas_rec_particles',
    leptons = ['papas_muons'],
    resonances = []
)

from heppy.analyzers.LeptonTreeProducer import LeptonTreeProducer
papas_muons_tree = cfg.Analyzer(
    LeptonTreeProducer,
    instance_label = 'papas',
    tree_name = 'events',
    tree_title = 'leptons',
    leptons = 'papas_muons'
)

from heppy.analyzers.ResonanceBuilder import ResonanceBuilder

gen_higgstojj = cfg.Analyzer(
    ResonanceBuilder,
    'gen_higgstojj',
    leg_collection = 'gen_jets_qcd',
    filter_func = lambda x : x.e()>10.,
    pdgid = 24,
)

rec_higgstojj = cfg.Analyzer(
    ResonanceBuilder,
    'rec_higgstojj',
    leg_collection = 'rec_jets_qcd',
    filter_func = lambda x : x.e()>10.,
    pdgid = 24,
)

from ROOT import gSystem
gSystem.Load("libdatamodel")
from eventstore import EventStore as Events

from heppy.analyzers.Filter import Filter
gen_jets_qcd = cfg.Analyzer(
    Filter,
    'gen_jets_qcd',
    input_objects = 'gen_jets',
    filter_func = lambda x : x.constituents[22].e()/x.e()<0.9
)

rec_jets_qcd = cfg.Analyzer(
    Filter,
    'rec_jets_qcd',
    input_objects = 'rec_jets',
    filter_func = lambda x : x.constituents[22].e()/x.e()<0.9
)

from heppy.fcc.analyzers.JetClusterizer import JetClusterizer
gen_jets = cfg.Analyzer(
    JetClusterizer,
    instance_label = 'gen',
    particles = 'gen_particles_for_jets'
)

rec_jets = cfg.Analyzer(
    JetClusterizer,
    instance_label = 'rec',
    particles = 'rec_particles_for_jets'
)

from heppy.analyzers.PapasSim import PFSim
from heppy.fcc.fastsim.detectors.CMS import CMS ### Change path!1!
papas = cfg.Analyzer(
    PFSim,
    instance_label = 'papas',
    detector = CMS(),
    gen_particles = 'gen_particles_stable',
    sim_particles = 'sim_particles',
    rec_particles = 'rec_particles',
    display = False,
    verbose = True
)

from heppy_fcc.analyzers.Matcher import Matcher
rec_jet_match = cfg.Analyzer(
    Matcher,
    instance_label = 'rec',
    match_particles = 'gen_jets',
    particles = 'rec_jets'
)

from heppy_fcc.analyzers.JetTreeProducer import JetTreeProducer
rec_jet_tree = cfg.Analyzer(
    JetTreeProducer,
    instance_label = 'papas',
    tree_name = 'events',
    tree_title = 'jets',
    jets = 'rec_jets'
)

from heppy_fcc.analyzers.MyHiggsTreeProducerPapas import MyHiggsTreeProducerPapas
rec_higgs_tree = cfg.Analyzer(
    MyHiggsTreeProducerPapas,
    tree_name = 'events',
    tree_title = 'higgs tree',
)

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
#    gen_ztomumu,
#    gen_ztoee,
#    gen_particles_for_jets,
#    gen_jets,
#    gen_jets_qcd,
#    gen_higgstojj,
#
    papas,
    papas_muons,
    rec_particles_for_jets,
    rec_jets,
    rec_jets_qcd,
    rec_higgstojj,
#    rec_jet_match,
    papas_muons_tree,
    rec_jet_tree,
    rec_higgs_tree,
    ] )

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    import random
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
    if len(sys.argv)==2:
        papas.display = True
        iev = int(sys.argv[1])

    loop = Looper( 'looper', config,
                   nEvents=100,
                   nPrint=0,
                   timeReport=True)
    simulation = None
    for ana in loop.analyzers:
        if hasattr(ana, 'display'):
            simulation = ana
    display = getattr(simulation, 'display', None)
    simulator = simulation.simulator
    detector = simulator.detector
    if iev is not None:
        process(iev)
    else:
        loop.loop()
        loop.write()
