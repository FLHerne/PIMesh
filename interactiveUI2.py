from network import EntityNetwork
import shutil
import os
import termcolor


print("\x1B[22t") # Save window title

MODE_LIST, MODE_LINKS, MODE_HELP = range(3)
mode_names = ["Entity List", "Single entity view", "Documentation"]
current_mode = MODE_LIST

print("\x1B]0;%s\x07" % "PIMesh") # Set window title

filename = "network0.pimesh"

network = EntityNetwork.from_file(filename)
current_entity = network["cabbage"]

status = "Started PIMesh"


def print_entity_list():
    global status
    for name in network:
        print(name)
    return len(network)


def print_entity_links(entity):
    print(str(entity))
    return len(current_entity.links)+4


def print_help():
    global status
    status = "Sorry, help not implemented yet"
    return 1


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
            current_mode = MODE_HELP
            status = "Entered help mode"
        elif command in ["list", "ls"]:
            current_mode = MODE_LIST
            status = "Entered entity list mode"
        elif command in ["view", "vw"]:
            current_mode = MODE_LINKS
            current_entity = network[arguments[0]]
            status = "Entered entity view mode"
        elif command in ["remove", "rm"]:
            if current_mode == MODE_LINKS:
                current_entity.unlink(arguments[0], arguments[1])
            else:
                status = "Please enter entity view mode using 'view <entity>' and try again"
        elif command in ["add", "ad"]:
            if current_mode == MODE_LINKS:
                current_entity.link(arguments[0], arguments[1])
            else:
                status = "Please enter entity view mode using 'view <entity>' and try again"
        elif command in ["update", "ud"]:
            if current_mode == MODE_LINKS:
                current_entity.relink(arguments[0], arguments[1], arguments[2])
            else:
                status = "Please enter entity view mode using 'view <entity>' and try again"
        else:
            status = "Error: Unknown command"
    except:
        status = command + ": Operation failed"


def vertical_padding(lines):
    output = ""
    for i in range(lines):
        output += "\n"
    return output


def horizontal_padding(cols):
    output = ""
    for i in range(cols):
        output += " "
    return output


quitting = False
while not quitting:
    cols, lines = shutil.get_terminal_size()
    os.system("clear")
    if current_mode == MODE_LIST:
        used_lines = print_entity_list()
    elif current_mode == MODE_LINKS:
        used_lines = print_entity_links(current_entity)
    elif current_mode == MODE_HELP:
        used_lines = print_help()
    else:
        status = "Error: Unknown current_mode!"

    used_lines += 2
    print(vertical_padding(lines-used_lines))
    termcolor.cprint(" " + status + horizontal_padding(cols-len(status)-1), attrs=['reverse'])
    command, arguments = split_input(input("> "))
    process_command(command, arguments)


os.system("clear")
try:
    network.to_file(filename)
    print("Saved session changes to file. \nPIMesh quitting...")
except:
    print("Saving to file failed!")

print("\x1B[23t")		#restore window title
