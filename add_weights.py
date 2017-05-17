#!/usr/bin/env python
from __future__ import division

import sys
import math
import progressbar
import ROOT
from ME_interface import ME_interface

if len(sys.argv) < 3:
    print("Usage: add_weights.py input_file out_file")
    sys.exit(2)

ROOT.gSystem.Load("libExRootAnalysis")
try:
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootClasses.h"')
except:
    print("Include failed. Exiting")
    sys.exit(1)

inname = sys.argv[1]
outname = sys.argv[2]

fin = ROOT.TFile(inname)
t = fin.Get("LHEF")
nentries = t.GetEntries()

param_files = ["000.dat", "100.dat", "010.dat", "001.dat", "-100.dat", "0-10.dat", "00-1.dat", "1-10.dat", "01-1.dat", "-101.dat"]
ME_calc = ME_interface("params")
ME_calc.import_list("../SubProcesses")
initialised = set()

import numpy
all_weights = numpy.zeros((nentries,len(param_files)))

print("%d entries in tree" % nentries)
print("-"*15)
print("Computing MEs")
print('-'*15)

for j, card in enumerate(param_files):
    print("Param card %d of %d: %s" % (j+1,len(param_files),card))
    #ME_calc.set_param_card(card)
    bar = progressbar.ProgressBar()
    for i in bar(range(nentries)):
        # Load selected branches with data from specified event
        #if i % (nentries//10) == 0: print("Event no.: %d - %d%% done." % (i, i/nentries*100))
        t.GetEntry(i)
        flavours = [par.PID for par in t.Particle if abs(par.PID) < 22]

        init = -1
        for k in (0,1):
            if (flavours[k] == 4 and flavours[(k+1)%2] != 2) or (abs(flavours[k])==4 and flavours[(k+1)%2] == 21): 
                flavours[k] /= 2
                init = k
                break
            if (abs(flavours[k]) == 3 and flavours[(k+1)%2] == 21) or flavours[k] == 3 and flavours[(k+1)%2] == -1:
                flavours[k] /= 3
                init = k
                break
        if flavours[0]==flavours[1]==21:
            for k, pid in enumerate(flavours[2:]):
                if abs(pid) == 3:
                    flavours[k+2] /= 3
                    flavours[flavours.index(-pid/3*4,2)] /= 2

        if init > -1:
            try:
                comp = {3:0, -3:0, 4:0, -4:0}
                for k, pid in enumerate(flavours[2:]): comp[pid] = k+2
                if i == 34: print init, flavours[init]*3/2, comp[flavours[init]*3/2]
                if abs(flavours[init]) == 1:
                    if comp[flavours[init]*3]: flavours[comp[flavours[init]*3]] /= 3
                    else: flavours[comp[flavours[init]*4]] /= 2
                else:            
                    if comp[flavours[init]*2]: flavours[comp[flavours[init]*2]] /= 2
                    elif comp[flavours[init]*3/2]: flavours[comp[flavours[init]*3/2]] /= 3
                    elif comp[-flavours[init]*2]: flavours[comp[-flavours[init]*2]] /= 2
                    elif comp[-flavours[init]*3/2]: flavours[comp[-flavours[init]*3/2]] /= 3
        
            except ValueError:
                print i, flavours
                import traceback
                traceback.print_exc()
                sys.exit(1)
        try:
            proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(ME_calc.pdg[f] for f in flavours))
        except KeyError:
            print i, flavours, init, comp
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        if proc not in ME_calc.mods:
            flavours[0], flavours[1] = flavours[1], flavours[0]
            proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(ME_calc.pdg[f] for f in flavours))
        try:
            if proc not in initialised:
                ME_calc.initialise(flavours, card)
                initialised.add(proc)
            p = [[par.Px, par.Py, par.Pz, par.E] for par in t.Particle if abs(par.PID) < 22]
            all_weights[i,j] = ME_calc.get_me((flavours,p))
        except KeyError:
            print i, flavours, proc
            import traceback
            traceback.print_exc()
            sys.exit(1)

    initialised.clear()
    print('\n')

fout = ROOT.TFile(outname, "RECREATE")
tout = t.CloneTree(0)#ROOT.TTree("LHEF", "Weighted events")

weights = ROOT.std.vector('double')(len(param_files), 0.)
tout.Branch("weights_true", weights)

print("-"*15)
print("Writing MEs to new tree")
print('-'*15)
bar = progressbar.ProgressBar()
for i in bar(range(nentries)):
    weights.clear()
    for j in range(len(param_files)):
        weights[j] = all_weights[i,j]
    tout.Fill()

tout.Write()
fout.Close()
