#!/usr/bin/env python3
#Top-level wrapper script for a general-purpose information-management tool

import sys
from network import Network
from cliui import UI

try:
  filename = sys.argv[1]
  networkfile = open(filename, 'r+')
  try:
      network = Network.from_file(networkfile)         # Note that this does not (and should not) create a new file
      print("Loaded PIMesh network from file")
  except FileNotFoundError:
      network = Network()
      print("Created empty network (file not found)")

  ui = UI(network)

  try:
      ui.run()
  except KeyboardInterrupt:
      print("Caught leopard interrupt")
      
  try:
      network.to_file(networkfile)
      print("Saved session changes to file.")
  except:
      print("Saving to file failed!")
     
except IndexError:
  print("Please specify filename as first argument.")
    
print("PIMesh quitting...")

