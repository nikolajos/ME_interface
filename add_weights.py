#!/usr/bin/env python
from __future__ import division

import sys
import math
import ROOT
from ME_interface import ME_interface

if len(sys.argv) < 3:
    print("Usage: add_weights.py input_file out_file")
    sys.exit(2)

ROOT.gSystem.Load("libExRootAnalysis")
try:
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootClasses.h"')
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootProgressBar.h"')
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

import numpy
all_weights = numpy.zeros((nentries,len(param_files)))

print("%d entries in tree" % nentries)
print("-"*15)
print("Computing MEs")
print('-'*15)

for j, card in enumerate(param_files):
    print("Param card %d of %d: %s" % (j,len(param_files),card))
    ME_calc.set_param_card(card)
    progressBar = ROOT.ExRootProgressBar(nentries)
    for i in range(nentries):
        # Load selected branches with data from specified event
        #if i % (nentries//10) == 0: print("Event no.: %d - %d%% done." % (i, i/nentries*100))
        t.GetEntry(i)
        flavours = [par.PID for par in t.Particle if abs(par.PID) != 24]
        proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(ME_calc.pdg[f] for f in flavours))
        if proc not in ME_calc.mods:
            flavours[0], flavours[1] = flavours[1], flavours[0]
            proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(ME_calc.pdg[f] for f in flavours))
        p = [[par.Px, par.Py, par.Pz, par.E] for par in t.Particle if abs(par.PID) != 24]
        all_weights[i,j] = ME_calc.get_me((flavours,p))
        
        progressBar.Update(i, i)
    progressBar.Update(i, i, ROOT.kTRUE)
    progressBar.Finish()
    print('\n')

fout = ROOT.TFile(outname, "RECREATE")
tout = t.CloneTree(0)#ROOT.TTree("LHEF", "Weighted events")

weights = ROOT.std.vector('double')(len(param_files), 0.)
tout.Branch("weights_true", weights)

progressBar = ROOT.ExRootProgressBar(nentries)
for i in range(nentries):
    weights.clear()
    for j in range(len(param_files)):
        weights[j] = all_weights[i,j]
    tout.Fill()
    progressBar.Update(i, i)

progressBar.Update(i, i, ROOT.kTRUE)
progressBar.Finish()

tout.Write()
fout.Close()
