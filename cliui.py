import shutil
import termcolor
import os
from enum import Enum


class UI:
  def __init__(self, network):
    self.network = network
    self.quitting = False
    
    self.Mode = Enum('Mode', ('list', 'links', 'help'))
    self.mode_names = {
	self.Mode.list: "Entity List",
	self.Mode.links: "Single entity view",
	self.Mode.help: "Documentation"
    }
    self.mode = self.Mode.list
    
    self.status = "Started PIMesh"
    self.cols, self.lines = shutil.get_terminal_size()
    
    self.commands = {
      "quit": self.command_quit,
      "exit": self.command_quit
    }
      
    #self.command_quit.names = ['quit', 'exit']
    #self.command_quit.accepted_args = [0]
    #self.command_quit.applicable_modes = [self.Mode.links, self.Mode.list, self.Mode.help]
    
  ###########
  def command_quit(self, mode, arguments):
      """Trigger a clean exit from the program, saving changes"""
      if len(arguments) != 0:
        return "Encountered " + str(len(arguments)) + " arguments, expected 0"
      self.quitting = True
      return 'Now quitting'
  
  ###########
  
  def processCommand(self):
    try:
      self.status = self.commands[self.command](self.mode, self.arguments)
    except KeyError:
      self.status = "Unknown command: " + self.command
      
  def split_input(self, user_input):
    """Split user input into a command and a list of arguments"""
    command, *arguments = user_input.split(" ", 1)
    if len(arguments) > 0:
        arguments = arguments[0].split(": ")
    return command, arguments
    
  def printStatusLine(self):
    self.status_line = " " + self.status + (" " * (self.cols - len(self.status) - 1))
    termcolor.cprint(self.status_line, attrs=['reverse'])
    
  def verticalPad(self):
    print("\n" * self.lines)
    
  def run(self):
    while not self.quitting:
      self.cols, self.lines = shutil.get_terminal_size()
      self.verticalPad()
      self.printStatusLine()
      self.command, self.arguments = self.split_input(input("> "))
      self.processCommand()
      os.system("clear")
    