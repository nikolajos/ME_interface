from __future__ import division
import sys
import math
import subprocess
import importlib

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

    # PDG codes used to identify correct lib.
    # Note that the same matrix elements are used for e and mu.
    pdg = {1:"d", -1:"dx", 2:"u", -2:"ux", 3:"s", -3:"sx", 4:"c", -4:"cx", 11:"em", -11:"ep", 12:"ve", -12:"vex", 13:"em", -13:"ep", 14:"ve", -14:"vex", 21:"g"}
    #pdg = {1:"d", -1:"dx", 2:"u", -2:"ux", 3:"d", -3:"dx", 4:"u", -4:"ux", 11:"em", -11:"ep", 12:"ve", -12:"vex", 13:"em", -13:"ep", 14:"ve", -14:"vex", 21:"g", 23:"", -24:"", 24:""}

    def __init__(self, param_dir=".", proc_dir="."):
        """Interface constructor. See class help text"""
        self.mods = None
        self.param_dir = param_dir
        self.param_card = "param_card.dat"
        self.proc_dir = proc_dir
        self.initialised = set()

    def set_param_card(self, name):
        """Sets parameter card to name and resets initialised processes."""
        self.param_card = name
        self.initialised.clear()
    
    def process_list(self, direc):
        """Constructs list of immediate subdirectories in direc"""
        dirs = subprocess.check_output(['find', direc, '-type', 'd', '-printf', "%f\n"])
        return (dirs.splitlines())[1:]

    def import_libs(self, direc = ''):
        """
        Imports matrix2py from all subdirectories of process directory. 
        Class process directory can be overwritten by input argument direc.
        """
        if not direc: direc = self.proc_dir
        procs = self.process_list(direc)
        sys.path = [direc] + sys.path
        self.mods = {proc:importlib.import_module(".matrix2py", proc) for proc in procs}
        #print(self.mods)


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
    
        # Construct dir name
        proc = "P1_%s%s_%s" % (self.pdg[pids[0]], self.pdg[pids[1]], ''.join((self.pdg[pid] for pid in pids[2:])))

        # Consider permutations of pids to find proc name
        if proc not in self.mods:
            pids[0], pids[1] = pids[1], pids[0]
            p[0], p[1] = p[1], p[0]
            proc = "P1_%s%s_%s" % (self.pdg[pids[0]], self.pdg[pids[1]], ''.join((self.pdg[pid] for pid in pids[2:])))
            if proc not in self.mods:
                for k, pid in enumerate(pids):
                    # Converts s/c to d/u
                    if abs(pid) == 3: pids[k] /= 3
                    elif abs(pid) == 4: pids[k] /= 2
                proc = "P1_%s%s_%s" % (self.pdg[pids[0]], self.pdg[pids[1]], ''.join((self.pdg[pid] for pid in pids[2:])))
                if proc not in self.mods:
                    pids[0], pids[1] = pids[1], pids[0]
                    p[0], p[1] = p[1], p[0]
                    proc = "P1_%s%s_%s" % (self.pdg[pids[0]], self.pdg[pids[1]], ''.join((self.pdg[pid] for pid in pids[2:])))
                
        try:
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
            print(proc)
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

        

    

