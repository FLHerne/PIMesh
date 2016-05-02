import os
import shutil
import termcolor

from enum import Enum
from network import EntityNetwork


print("\x1B[22t") # Save window title

Mode = Enum('Mode', ('list', 'links', 'help'))
mode_names = {
    Mode.list: "Entity List",
    Mode.links: "Single entity view",
    Mode.help: "Documentation"
}
current_mode = Mode.list

print("\x1B]0;%s\x07" % "PIMesh") # Set window title

filename = "network0.pimesh"            # Currently fixed filename - should it really be an argument when starting the script?

try:
    network = EntityNetwork.from_file(filename)         # Note that this does not (and should not) create a new file
    status = "Loaded PIMesh network from file"
except FileNotFoundError:
    network = EntityNetwork()
    status = "Created empty network (file not found)"

#class command:
#  def __init__(self, name, invocations, modes, minargs, maxargs)
#    self.name = name
#    self.invocations = invocations
#    self.modes = modes
#    self.minargs = minargs
#    self.maxargs = maxargs
#  def __call__(self):
#    outcome = "just testing"
#    return (name + ": " + outcome)


def print_entity_list():
    """Print a list of entitites which have one of more links to/from them"""
    global status
    if len(network) == 0:
        print("(No entities in network)")           # Could be slightly confusing, but saves a big empty space
        return 1
    for name in network:
        print(name)
    return len(network)         # number of lines printed by this function, needed to pad vertically by the right amount


def print_entity_links(entity):
    """Print a list of links associated with a specific entity"""
    print(str(entity))
    return len(entity.links)+3 # number of lines printed by this function, needed to pad vertically by the right amount


def print_help():
    """Display documentation"""
    global status
    status = "Sorry, help not implemented yet"          # FIXME
    return 0                    # number of lines printed by this function, needed to pad vertically by the right amount


def split_input(user_input):
    """Split user input into a command and a list of arguments"""
    command, *arguments = user_input.split(" ", 1)
    if len(arguments) > 0:
        arguments = arguments[0].split(": ")
    return command, arguments

#-----------------

def command_quit(arguments):
    global quitting
    quitting = True
    return "Now quitting"

command_quit.names = ['quit', 'exit']
command_quit.accepted_args = [0]
command_quit.applicable_modes = [Mode.links, Mode.list, Mode.help]

def command_list(arguments):
    global current_mode
    current_mode = Mode.list
    #current_entity.link(arguments[0], arguments[1])
    return "Now listing all entities"

command_list.names = ['list', 'ls']
command_list.accepted_args = [0]
command_list.applicable_modes = [Mode.links, Mode.help]

def command_view(arguments):
    global current_mode, current_entity
    current_mode = Mode.links
    current_entity = network[arguments[0]]
    #current_entity.link(arguments[0], arguments[1])
    return "Now viewing entity: " + arguments[0]

command_view.names = ['view', 'vw']
command_view.accepted_args = [1]
command_view.applicable_modes = [Mode.links, Mode.help, Mode.list]

#-----------------

commands = (
    command_list,
    command_view,
    command_quit
)


def process_command(command, arguments):                #FIXME
    """Act on a command and list of arguments - this needs improving"""
    global quitting, current_mode, current_entity, status       # Not sure if globals are nice or not...
    
    invocation = command
    for command in commands:
        if invocation in command.names:
            if len(arguments) not in command.accepted_args:
                status = invocation + ": Unacceptable number of arguments"
                break
            if current_mode not in command.applicable_modes:
                status = invocation + ": Inappropriate mode"
                break
            status = command(arguments)
            break
    else:
        status = invocation + " - unknown command"
    #for command in commands:
    #if invocation in command.invocations:
        #status = command()
        #break
    #else:
    #status = invocation + " - unknown command"


    #status = command + ": Operation sucessful"          # Fallback status - is assuming sucess really a good idea?
    #try:                                                # Hacky way to catch errors - will be fixed in new code (commented out)
    #    if command in ["quit", "exit"]:
    #        status = "Exiting by user request..."
    #        quitting = True
    #    elif command in ["help", "?", "man", "manual"]:
    #        current_mode = Mode.help
    #        status = "Entered help mode"
    #    elif command in ["list", "ls"]:
    #        current_mode = Mode.list
    #        status = "Entered entity list mode"
    #    elif command in ["view", "vw"]:
    #        current_mode = Mode.links
    #        current_entity = network[arguments[0]]
    #        status = "Now viewing entity: " + arguments[0]
    #    elif command in ["remove", "rm"]:
    #        if current_mode == Mode.links:
    #            current_entity.unlink(arguments[0], arguments[1])
    #        else:
    #            status = "Please enter entity view mode using 'view <entity>' and try again"
    #    elif command in ["add", "ad"]:
    #        if current_mode == Mode.links:
    #            current_entity.link(arguments[0], arguments[1])
    #        else:
    #            status = "Please enter entity view mode using 'view <entity>' and try again"
    #    elif command in ["update", "ud"]:
    #        if current_mode == Mode.links:
    #            current_entity.relink(arguments[0], arguments[1], arguments[2])
    #        else:
    #            status = "Please enter entity view mode using 'view <entity>' and try again"
    #    else:
    #        status = "Error: Unknown command"
    #except:
    #    status = command + ": Operation failed"


quitting = False
while not quitting:
    cols, lines = shutil.get_terminal_size()
    os.system("clear")
    if current_mode == Mode.list:               # Elif chains are ugly - FIXME
        used_lines = print_entity_list()
    elif current_mode == Mode.links:
        used_lines = print_entity_links(current_entity)
    elif current_mode == Mode.help:
        used_lines = print_help()
    else:
        status = "Error: Unknown current_mode!"

    used_lines += 3
    print("\n" * (lines - used_lines))            # Pad vertically so that the command prompt is at the bottom of the terminal
    status_line = " " + status + (" " * (cols - len(status) - 1))
    termcolor.cprint(status_line, attrs=['reverse'])
    command, arguments = split_input(input("> "))
    process_command(command, arguments)


os.system("clear")
try:
    network.to_file(filename)
    print("Saved session changes to file. \nPIMesh quitting...")
except:
    print("Saving to file failed!")

print("\x1B[23t")		#restore window title
