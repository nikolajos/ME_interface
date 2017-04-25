from __future__ import division
import subprocess
import importlib

if __name__ == "__main__":
    raise RuntimeError("This is only supposed to be used as a module")

class ME_interface(object):
    """Collection of methods for interfacing with MadGraph standalone matrix elements"""


    def __init__(self):
        # PDG codes used to identify correct lib.
        # Note that the same matrix elements are used for e and mu.
        self.pdg = {1:"d", -1:"dx", 2:"u", -2:"ux", 3:"s", -3:"sx", 4:"c", -4:"cx", 11:"em", -11:"ep", 12:"ve", -12:"vex", 13:"em", -13:"ep", 14:"ve", -14:"vex"}
        self.mods = None

    def process_list(self, direc):
        """Constructs list of immediate subdirectories in direc"""
        dirs = subprocess.check_output(['find', direc, '-type', 'd', '-printf', "%f\n"])
        return (dirs.splitlines())[1:]

    def import_list(self, direc = '.'):
        """Imports matrix2py from all subdirectories in direc"""
        procs = process_list(direc)
        self.mods = {proc:importlib.import_module(".matrix2py", proc) for proc in procs}


    def invert_momenta(self, p):
        """Converter momentum table from C to fortran order"""
        new_p = [[0 for j in p] for i in p[0]]
        for i, onep in enumerate(p):
            for j, x in enumerate(onep):
                new_p[j][i] = x

    def get_me(self, ev):
        """Parton level ME using flavours and momenta from ev"""
    
        # Construct dir name
        flavour = "P1_%s%s_%s%s%s%s%s%s" % (tuple(self.pdg[pid] for pid in ev[0]))

    

