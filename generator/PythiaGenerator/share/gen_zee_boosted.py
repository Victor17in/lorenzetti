#!/usr/bin/env python3
from Gaugi.messenger    import LoggingLevel, Logger
from Gaugi              import GeV
import argparse
import sys,os


mainLogger = Logger.getModuleLogger("pythia")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

#
# Mandatory arguments
#


parser.add_argument('-o','--outputFile', action='store', dest='outputFile', required = True,
                    help = "The event file generated by pythia.")

parser.add_argument('--evt','--numberOfEvents', action='store', dest='numberOfEvents', required = True, type=int, default=1,
                    help = "The number of events to be generated.")

#
# Pileup simulation arguments
#

parser.add_argument('--pileupAvg', action='store', dest='pileupAvg', required = False, type=int, default=40,
                    help = "The pileup average (default is zero).")

parser.add_argument('--bc_id_start', action='store', dest='bc_id_start', required = False, type=int, default=-21,
                    help = "The bunch crossing id start.")

parser.add_argument('--bc_id_end', action='store', dest='bc_id_end', required = False, type=int, default=4,
                    help = "The bunch crossing id end.")

parser.add_argument('--bc_duration', action='store', dest='bc_duration', required = False, type=int, default=25,
                    help = "The bunch crossing duration (in nanoseconds).")


#
# Extra parameters
#

parser.add_argument('--outputLevel', action='store', dest='outputLevel', required = False, type=int, default=0,
                    help = "The output level messenger.")

parser.add_argument('-s','--seed', action='store', dest='seed', required = False, type=int, default=0,
                    help = "The pythia seed (zero is the clock system)")




if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()

try:

  minbias_file = os.environ['LZT_PATH']+'/generator/PythiaGenerator/data/minbias_config.cmnd'
  main_file = os.environ['LZT_PATH']+'/generator/PythiaGenerator/data/zee_config.cmnd'
  
  from P8Kernel import EventGenerator
  
  # The pythia generator!
  gen = EventGenerator( "EventGenerator", OutputFile = args.outputFile)
  
  from PythiaGenerator import Pileup
  
  # Pileup generator
  pileup = Pileup( "MinimumBias",
                   File           = minbias_file,
                   EtaMax         = 3.2,
                   Select         = 2,
                   PileupAvg      = args.pileupAvg,
                   BunchIdStart   = args.bc_id_start,
                   BunchIdEnd     = args.bc_id_end,
                   OutputLevel    = args.outputLevel,
                   Seed           = args.seed,
                   DeltaEta       = 0.22,
                   DeltaPhi       = 0.22,
                   )
  
  # To collect using this cell position
  from PythiaGenerator import Zee
  
  # Create the Zee events
  zee = Zee( "Zee",
            File        = main_file,
            EtaMax      = 3.2,
            MinPt       = 15*GeV,
            Seed        = args.seed,
            OutputLevel = args.outputLevel,
           )
  
  from PythiaGenerator import BoostedEvents, Particle
  # Add boosted events
  boostedElectron = BoostedEvents( "ElectronBoosted", 
                                   Particle=Particle.Electron, 
                                   DeltaR=0.5,
                                   Seed = args.seed,
                                   OutputLevel = args.outputLevel
                                   )
  
  # Z->ee
  gen+=zee
  # Z->ee + e
  gen+=boostedElectron
  # Z->ee + e + minbias
  gen+=pileup
  # Run!
  gen.run(args.numberOfEvents)

  sys.exit(0)
except  Exception as e:
  print(e)
  sys.exit(1)
