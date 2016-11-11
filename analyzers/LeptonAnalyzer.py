from heppy.framework.analyzer import Analyzer
from heppy.utils.deltar import matchObjectCollection, deltaR
from heppy.particles.isolation import Circle, Isolation

class LeptonAnalyzer(Analyzer):

    def beginLoop(self, setup):
        super(LeptonAnalyzer, self).beginLoop(setup)
        self.iso_cone = Circle(0.4)

    def process(self, event):
        particles = getattr(event, self.cfg_ana.particles)
        sel_leptons = [ptc for ptc in particles if self.sel_lepton(ptc)]
        pdgids = [211, 22, 130]
        for lepton in sel_leptons:
            for pdgid in pdgids:
                self.set_isolation(lepton, particles, pdgid)
        setattr(event, self.instance_label, sel_leptons)

    def sel_lepton(self, ptc):
        if abs(ptc.pdgid()) == self.cfg_ana.pdgid:
            return True

    def set_isolation(self, lepton, particles, pdgid):
        sel_ptcs = [ptc for ptc in particles if ptc.pdgid()==pdgid]
        iso = Isolation(lepton, sel_ptcs, [self.iso_cone], label=str(pdgid))
        setattr(lepton, 'iso_{pdgid}'.format(pdgid=pdgid), iso)
