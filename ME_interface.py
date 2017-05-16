from __future__ import division
import sys
import subprocess
import importlib

if __name__ == "__main__":
    raise RuntimeError("This is only supposed to be used as a module")

class ME_interface(object):
    """Collection of methods for interfacing with MadGraph standalone matrix elements"""

    # PDG codes used to identify correct lib.
    # Note that the same matrix elements are used for e and mu.
#    pdg = {1:"d", -1:"dx", 2:"u", -2:"ux", 3:"s", -3:"sx", 4:"c", -4:"cx", 11:"em", -11:"ep", 12:"ve", -12:"vex", 13:"em", -13:"ep", 14:"ve", -14:"vex", 21:"g"}
    pdg = {1:"d", -1:"dx", 2:"u", -2:"ux", 3:"d", -3:"dx", 4:"u", -4:"ux", 11:"em", -11:"ep", 12:"ve", -12:"vex", 13:"em", -13:"ep", 14:"ve", -14:"vex", 21:"g"}

    def __init__(self, path=""):
        """Interface constructor. Optionally sets path to parameter card directory"""
        self.mods = None
        self.param_dir = path
        self.param_card = "param_card.dat"

    def set_param_card(self, name):
        """Updates current param card"""
        self.param_card = name
        if self.mods: self.initialise_all()
        
    def initialise_all(self):
        """Initialises all modules with current param card"""
        if self.mods:
            for proc in self.mods:
                self.mods[proc].initialise(self.param_dir+'/'+self.param_card)
        else: print("Warning: Tried to initialise empty module list")

    def initialise(self, flavours, card=""):
        """Initialises library given by list of pdg codes flavours"""
        proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(self.pdg[pid] for pid in flavours))
        if card:
            name = card
        else: 
            name = self.param_card
        self.mods[proc].initialise(self.param_dir+'/'+name)
    
    def process_list(self, direc):
        """Constructs list of immediate subdirectories in direc"""
        dirs = subprocess.check_output(['find', direc, '-type', 'd', '-printf', "%f\n"])
        return (dirs.splitlines())[1:]

    def import_list(self, direc = '.'):
        """Imports matrix2py from all subdirectories in direc"""
        procs = self.process_list(direc)
        sys.path = [direc] + sys.path
        self.mods = {proc:importlib.import_module(".matrix2py", proc) for proc in procs}
        #print(self.mods)


    def invert_momenta(self, p):
        """Converter momentum table from C to fortran order"""
        new_p = [[0 for j in p] for i in p[0]]
        for i, onep in enumerate(p):
            for j, x in enumerate(onep):
                new_p[j][i] = x
        return new_p

    def get_me(self, ev):
        """Parton level ME using flavours and momenta from ev"""
    
        # Construct dir name
        flavour = "P1_%s%s_%s%s%s%s%s%s" % (tuple(self.pdg[pid] for pid in ev[0]))

        P = self.invert_momenta(ev[1])
        alphas = 0.18 # Strong coupling
        return self.mods[flavour].get_me(P, alphas, 0) # 0 => sum over helicities

    

