from network import EntityNetwork
import shutil
import os
import termcolor

print("\x1B[22t") 			#Save window title

listMode, linksMode, helpMode = range(0, 3)
modeNames = ["Entity List", "Single entity view", "Documentation"]
viewingMode = listMode

print("\x1B]0;%s\x07" % "PIMesh") 

filename = "network0.pimesh"

network = EntityNetwork.from_file(filename)
currentEntityName = "cabbage"

status = "Started PIMesh"

def printEntityList(network):
  global status
  try:
    for name in network:
      print(name)
    return len(network)
  except:
    status = "Error encountered while printing entity list"
    return 3

    
def printEntityLinks(entity):
  print(str(entity))
  return len(network[currentEntityName].links)+4
  
def printHelp():
  global status
  status = "Sorry, help not implemented yet"
  return 1
  
def splitInput(userInput):
  command, *arguments = userInput.split(" ", 1)
  if len(arguments) > 0:
    arguments = arguments[0].split(": ")
  return command, arguments

def processCommand(command, arguments):
  global quiting, viewingMode, currentEntityName, status
  status = command + ": Operation sucessful"
  try:
    if command in ["quit", "exit"]:
      status = "Exiting by user request..."
      quiting = True
    elif command in ["help", "?", "man", "manual"]:
      viewingMode = helpMode
      status = "Entered help mode"
    elif command in ["list", "ls"]:
      viewingMode = listMode
      status = "Entered entity list mode"
    elif command in ["view", "vw"]:
      viewingMode = linksMode
      currentEntityName = arguments[0]
      status = "Entered entity view mode"

    elif command in ["remove", "rm"]:
      if viewingMode == linksMode:
        network[currentEntityName].unlink(arguments[0], arguments[1])
      else:
        status = "Please enter entity view mode using 'view <entity>' and try again"
    elif command in ["add", "ad"]:
      if viewingMode == linksMode:
        network[currentEntityName].link(arguments[0], arguments[1])
      else:
        status = "Please enter entity view mode using 'view <entity>' and try again"
    elif command in ["update", "ud"]:
      if viewingMode == linksMode:
        network[currentEntityName].relink(arguments[0], arguments[1], arguments[2])
      else:
        status = "Please enter entity view mode using 'view <entity>' and try again"
      
    else:
      status = "Error: Unknown command"
  except:
    status = command + ": Operation failed"
    
def verticalPad(lines):
  output = ""
  for i in range(lines):
    output += "\n"
  return output
    
def horizontalPad(cols):
  output = ""
  for i in range(cols):
    output += " "
  return output


    
quiting = False
while not quiting:
  
  cols, lines = shutil.get_terminal_size()
  os.system("clear")
  if viewingMode == listMode:
    usedLines = printEntityList(network)
  elif viewingMode == linksMode:
    usedLines = printEntityLinks(network[currentEntityName])
  elif viewingMode == helpMode:
    usedLines = printHelp()
  else:
    status = "Error: Unknown viewingMode!"

  usedLines += 2
  print(verticalPad(lines-usedLines))
  termcolor.cprint(" " + status + horizontalPad(cols-len(status)-1), attrs=['reverse'])
  command, arguments = splitInput(input("> "))
  processCommand(command, arguments)


os.system("clear")
try:
  network.to_file(filename)
  print("Saved session changes to file. \nPIMesh quitting...")
except:
  print("Saving to file failed!")
  
  print("\x1B[23t")		#restore window title