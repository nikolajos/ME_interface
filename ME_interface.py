from __future__ import division
import sys
import math
import os.path
import importlib
from collections import Counter

if __name__ == "__main__":
    raise RuntimeError("This is only supposed to be used as a module")

class ME_interface(object):
    """
    Collection of methods for interfacing with MadGraph standalone matrix 
    elements. ME_interface(param_dir='.', proc_dir='.') constructs the 
    object. 
     - param_dir specifies the location of parameter cards. 
     - proc_dir should point to the SubProcesses directory.

    Basic usage:
     - First do import_lib() to import and create list of libraries
     - Then do set_param_card(name) to specify parameters
     - For each event use get_me(pids, p) to get amplitude
     - (optionally) Go to step two to change parameters
    """

    def __init__(self, param_dir=".", proc_dir="."):
        """Interface constructor. See class help text"""
        self.mods = dict()
        self.aliases = dict()
        self.param_dir = param_dir
        self.param_card = "param_card.dat"
        self.proc_dir = proc_dir
        self.initialised = set()
        # PDG codes used to identify correct lib.
        # Note that the same matrix elements are used for e and mu.
        #self.pdg = {1:"d", -1:"dx", 2:"u", -2:"ux", 3:"s", -3:"sx", 4:"c", -4:"cx", 11:"em", -11:"ep", 12:"ve", -12:"vex", 13:"em", -13:"ep", 14:"ve", -14:"vex", 21:"g"}
        #pdg = {1:"d", -1:"dx", 2:"u", -2:"ux", 3:"d", -3:"dx", 4:"u", -4:"ux", 11:"em", -11:"ep", 12:"ve", -12:"vex", 13:"em", -13:"ep", 14:"ve", -14:"vex", 21:"g", 23:"", -24:"", 24:""}

    def set_param_card(self, name):
        """Sets parameter card to name and resets initialised processes."""
        self.param_card = name
        self.initialised.clear()
    
    def import_libs(self):
        """
        Imports matrix2py from all subdirectories of process directory. 
        Class process directory can be overwritten by input argument direc.
        """
        if not os.path.exists('index'):
            from extract_process import create_index
            create_index(self.proc_dir)

        sys.path = [self.proc_dir] + sys.path

        with open('index', 'r') as idx:
            for line in idx:
                proc = line.split(',')
                self.mods[proc[0]] = importlib.import_module(".matrix2py", proc[0])
                subs = [[int(e) for e in sub.split(' ')] for sub in proc[1:]]
                for sub in subs:
                    self.aliases[ (tuple(sorted(sub[:2])), tuple(sorted(sub[2:]))) ] = proc[0]

        #self.mods = {proc:importlib.import_module(".matrix2py", proc) for proc in procs}



    def invert_momenta(self, p):
        """Converts momentum table from C to fortran order"""
        new_p = [[0 for j in p] for i in p[0]]
        for i, onep in enumerate(p):
            for j, x in enumerate(onep):
                new_p[j][i] = x
        return new_p

    def get_me(self, pids, p):
        """
        Computes parton level amplitude using input particle ids and 
        four-momenta. 
           - pids is a sequence containing pdg codes of all participating 
             particles. The first two defines the initial state and the rest 
             are final state.
           - p is a list of four-momenta for said particles. These should be in 
             C-order, i.e. one p[0] is a list giving the four-momentum of the 
             first initial state particle, p[1] the four-momentum of the second 
             and so on.
           - returns ME at point in phase-space defined by p.
        """
        try:
            proc = self.aliases[ (tuple(sorted(pids[:2])), tuple(sorted(pids[2:]))) ]
            # Ensures that library is initialised to current parameters
            if proc not in self.initialised:
                self.mods[proc].initialise(self.param_dir+'/'+self.param_card)
                self.initialised.add(proc)
            P = self.invert_momenta(p) # C- to fortran-order
            alphas = 0.18 # Strong coupling
            me = self.mods[proc].get_me(P, alphas, 0) # 0 => sum over helicities
            if math.isnan(me): raise ValueError("Got NaN at evt., param card %s" % (self.param_card))
            return me
        except KeyError:
            print("Unable to find matching library for process. Tried combination: ")
            print(pids)
            print(self.aliases.keys())
            import traceback
            traceback.print_exc()
            raise KeyError
        except ValueError:
            print("Invalid ME value for event with pids and momenta: ")
            print(pids)
            for par in p:
                print(par)
            import traceback
            traceback.print_exc()
            raise ValueError

        

    

