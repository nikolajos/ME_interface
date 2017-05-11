#!/usr/bin/env python
from __future__ import division

import sys
import math
import ROOT

if len(sys.argv) < 3:
    print(" Usage: add_weights.py input_file output_file")
    sys.exit(2)

ROOT.gSystem.Load("libExRootAnalysis")
try:
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootClasses.h"')
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootTreeReader.h"')
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootTreeWriter.h"')
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootTreeBranch.h"')
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootProgressBar.h"')
except:
    print("Include failed. Exiting")
    sys.exit(1)

inname = sys.argv[1]
outname = sys.argv[2]

# Create chain of root trees
chain = ROOT.TChain("LHEF")
chain.Add(inname)

# Create object of class ExRootTreeReader
treeReader = ROOT.ExRootTreeReader(chain)
numberOfEntries = treeReader.GetEntries()

# Get pointers to branches used in this analysis
eventin = treeReader.UseBranch("Event")
particlesin = treeReader.UseBranch("Particle")

try:
    outfile = ROOT.TFile.Open(outname, "RECREATE")
except:
    print("Failed to open %s" % outname)
    sys.exit(1)
treeWriter = ROOT.ExRootTreeWriter(outfile, "MC_TRUTH")

branchEvent = treeWriter.NewBranch("Event", ROOT.TRootLHEFEvent.Class())
branchParticle = treeWriter.NewBranch("Particle", ROOT.TRootLHEFParticle.Class())
branchWeights = treeWriter.NewBranch("Weight", ROOT.TRootWeight.Class())

progressBar = ROOT.ExRootProgressBar(numberOfEntries)
treeWriter.Clear()
for entry in range(0, numberOfEntries):
    # Load selected branches with data from specified event
    treeReader.ReadEntry(entry)

    event = branchEvent.NewEntry()
    event.Number = eventin.Number
    event.Nparticles = eventin.Nparticles
    event.ProcessID = eventin.ProcessID
    event.Weight = eventin.Weight
    event.ScalePDF = eventin.ScalePDF
    event.CouplingQED = eventin.CouplingQED
    event.CouplingQCD = evntin.CouplingQCD

    
    
    
    treeWriter.Clear()
