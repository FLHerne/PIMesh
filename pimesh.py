import sys
from network import Network
from cliui import UI

filename = sys.argv[1]

try:
    network = Network.from_file(filename)         # Note that this does not (and should not) create a new file
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
    network.to_file(filename)
    print("Saved session changes to file.")
except:
    print("Saving to file failed!")
    
print("PIMesh quitting...")

