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

filename = "network0.pimesh"

network = EntityNetwork.from_file(filename)
current_entity = network["cabbage"]

status = "Started PIMesh"


def print_entity_list():
    for name in network:
        print(name)
    return len(network)


def print_entity_links(entity):
    print(str(entity))
    return len(entity.links)+3


def print_help():
    global status
    status = "Sorry, help not implemented yet"
    return 0


def split_input(user_input):
    command, *arguments = user_input.split(" ", 1)
    if len(arguments) > 0:
        arguments = arguments[0].split(": ")
    return command, arguments


def process_command(command, arguments):
    global quitting, current_mode, current_entity, status
    status = command + ": Operation sucessful"
    try:
        if command in ["quit", "exit"]:
            status = "Exiting by user request..."
            quitting = True
        elif command in ["help", "?", "man", "manual"]:
            current_mode = Mode.help
            status = "Entered help mode"
        elif command in ["list", "ls"]:
            current_mode = Mode.list
            status = "Entered entity list mode"
        elif command in ["view", "vw"]:
            current_mode = Mode.links
            current_entity = network[arguments[0]]
            status = "Now viewing entity: " + arguments[0]
        elif command in ["remove", "rm"]:
            if current_mode == Mode.links:
                current_entity.unlink(arguments[0], arguments[1])
            else:
                status = "Please enter entity view mode using 'view <entity>' and try again"
        elif command in ["add", "ad"]:
            if current_mode == Mode.links:
                current_entity.link(arguments[0], arguments[1])
            else:
                status = "Please enter entity view mode using 'view <entity>' and try again"
        elif command in ["update", "ud"]:
            if current_mode == Mode.links:
                current_entity.relink(arguments[0], arguments[1], arguments[2])
            else:
                status = "Please enter entity view mode using 'view <entity>' and try again"
        else:
            status = "Error: Unknown command"
    except:
        status = command + ": Operation failed"


quitting = False
while not quitting:
    cols, lines = shutil.get_terminal_size()
    os.system("clear")
    if current_mode == Mode.list:
        used_lines = print_entity_list()
    elif current_mode == Mode.links:
        used_lines = print_entity_links(current_entity)
    elif current_mode == Mode.help:
        used_lines = print_help()
    else:
        status = "Error: Unknown current_mode!"

    used_lines += 3
    print("\n" * (lines - used_lines))
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
