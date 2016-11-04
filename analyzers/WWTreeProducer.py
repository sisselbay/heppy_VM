from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

# Edit of ZHTreeProducer to WW->had+lep
class WWTreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(WWTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'mytree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        bookParticle(self.tree, 'W1')
        bookParticle(self.tree, 'W2')
        #bookParticle(self.tree, 'recoil')
        bookJet(self.tree, 'W1_1')
        bookJet(self.tree, 'W1_2')
        #bookJet(self.tree, 'jet3')
        #bookJet(self.tree, 'jet4')
        bookLepton(self.tree, 'W2_1')
        bookLepton(self.tree, 'W2_2')
        #bookParticle(self.tree, 'higgs')
        #bookParticle(self.tree, 'higgs_1')
        #bookParticle(self.tree, 'higgs_2')
        #bookParticle(self.tree, 'misenergy')
       
    def process(self, event):
        self.tree.reset()
        #recoil = getattr(event, self.cfg_ana.recoil)
        #fillParticle(self.tree, 'recoil', recoil)        
        #misenergy = getattr(event, self.cfg_ana.misenergy)
        #fillParticle(self.tree, 'misenergy', misenergy )        

#        zeds = getattr(event, self.cfg_ana.zeds)
#        if len(zeds)>0:
#            zed = zeds[0]
#            fillParticle(self.tree, 'zed', zed)
#            fillJet(self.tree, 'zed_1', zed.legs[0])
#            fillJet(self.tree, 'zed_2', zed.legs[1])

        #jets = getattr(event, self.cfg_ana.jets)
        #for ijet, jet in enumerate(jets):
        #    if ijet==4:
        #        break
        #    fillJet(self.tree, 'jet{ijet}'.format(ijet=ijet+1), jet)
        #higgses = getattr(event, self.cfg_ana.higgses)
        #if len(higgses)>0:
        #    higgs = higgses[0]
        #    fillParticle(self.tree, 'higgs', higgs)
        #    fillLepton(self.tree, 'higgs_1', higgs.legs[0])
        #    fillLepton(self.tree, 'higgs_2', higgs.legs[1])
        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        
