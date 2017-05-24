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
    if j > 1: break
    print("Param card %d of %d: %s" % (j+1,len(param_files),card))
    #ME_calc.set_param_card(card)
    bar = progressbar.ProgressBar()
    for i in bar(range(500)):
        # Load selected branches with data from specified event
        #if i % (nentries//10) == 0: print("Event no.: %d - %d%% done." % (i, i/nentries*100))
        t.GetEntry(i)
        flavours = [par.PID for par in t.Particle if abs(par.PID) < 22]
        p = [[par.Px, par.Py, par.Pz, par.E] for par in t.Particle if abs(par.PID) < 22]

        proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(ME_calc.pdg[f] for f in flavours))
        
        if proc not in ME_calc.mods:
            flavours[0], flavours[1] = flavours[1], flavours[0]
            p[0], p[1] = p[1], p[0]
            proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(ME_calc.pdg[f] for f in flavours))
            if proc not in ME_calc.mods:
                for k, pid in enumerate(flavours):
                    if abs(pid) == 3: flavours[k] /= 3
                    elif abs(pid) == 4: flavours[k] /= 2
                proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(ME_calc.pdg[f] for f in flavours))
                if proc not in ME_calc.mods:
                    flavours[0], flavours[1] = flavours[1], flavours[0]
                    p[0], p[1] = p[1], p[0]
                    proc = "P1_%s%s_%s%s%s%s%s%s" % (tuple(ME_calc.pdg[f] for f in flavours))
                
        try:
            if proc not in initialised:
                ME_calc.initialise(flavours, card)
                initialised.add(proc)
            me = ME_calc.get_me((flavours,p))
            if math.isnan(me): raise ValueError("Got NaN at evt. %d, param card no. %d" % (i,j))
            all_weights[i,j] = me
        except KeyError:
            print i, flavours, proc
            import traceback
            traceback.print_exc()
            sys.exit(1)
        except ValueError:
            print [par.PID for par in t.Particle if abs(par.PID) < 22], flavours
            for par in p:
                print par
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
for i in bar(range(500)):
    #weights.clear()
    for j in range(2):#len(param_files)):
        weights[j] = all_weights[i,j]
        if i == 0: print weights[j]
    tout.Fill()

tout.Write()
fout.Close()
