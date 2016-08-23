#!/usr/bin/env python3
#Top-level wrapper script for a general-purpose information-management tool

import sys
from network import Network
from cliui import UI

try:
    filename = sys.argv[1]
    try:
        networkfile = open(filename, 'r+')
        # Note that this does not (and should not) create a new file
        network = Network.from_file(networkfile)
        print("Loaded PIMesh network from file")
    except FileNotFoundError:
        networkfile = open(filename, 'w')
        network = Network()
        print("Created empty network (file not found)")

    ui = UI(network)

    try:
        ui.run()
    except KeyboardInterrupt:
        print("Caught leopard interrupt")

    networkfile.seek(0)
    try:
        network.to_file(networkfile)
        networkfile.truncate()
        print("Saved session changes to file.")
    except:
        print("Saving to file failed!")
    networkfile.close()

except IndexError:
    print("Please specify filename as first argument.")

print("PIMesh quitting...")

