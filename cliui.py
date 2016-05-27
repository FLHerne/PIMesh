import shutil
import termcolor
import os
from enum import Enum


class UI:
  Mode = Enum('Mode', ('list', 'links', 'help', 'duck'))
  mode_names = {
    Mode.list: "List of all entities",
    Mode.links: "Single entity view",
    Mode.help: "Documentation",
    Mode.duck: "Anatid"
  }
  
 
  def __init__(self, network):
    self.network = network
    self.quitting = False
    
    self.mode = self.Mode.list
    
    self.status = "Started PIMesh"
    self.cols, self.lines = shutil.get_terminal_size()
    
    self.used_lines = 0
    
    self.commands = {
      "duck": self.command_duck,
      "list": self.command_list,
      "view": self.command_view,
      "help": self.command_help,
      "quit": self.command_quit,
    }
    
    self.mode_content = {
      UI.Mode.list: self.list_print,
      UI.Mode.links: self.links_print,
      UI.Mode.help: self.help_print,
      UI.Mode.duck: self.duck_print
    }
      
  def list_print(self):	
    """Print a list of every entity involved in one of more links"""
    for entity in self.network.targets:
      print(entity)
    return len(self.network.targets)
  
  def links_print(self):	
    print("links go here")
    return 1  
  
  def help_print(self):
    """Display the docstrings for all commands"""
    for command in self.commands.items():
      print(command[0])
      print("  " + command[1].__doc__ + '\n')
    return len(self.commands)*3
  
  def duck_print(self):	
    print("\n   >(')____, \n    (` =~~/  \n ~^~^`---'~^~^~")
    return 4
      
  ###########
  def command_duck(self, mode, arguments):
    """Draw a duck"""
    self.mode = self.Mode.duck
    return("Quack!")
  
  def command_list(self, mode, arguments):
    """Print a list of every entity involved in one of more links"""
    self.mode = self.Mode.list
    return("Now entering list mode")
  
  def command_help(self, mode, arguments):
    """List and describe all commands"""
    self.mode = self.Mode.help
    return("Now veiwing documentation")
  
  def command_view(self, mode, arguments):
    """View a specific entity"""
    self.mode = self.Mode.links
    return("Now entering entity links mode")
  
  def command_quit(self, mode, arguments):
      """Trigger a clean exit from the program, saving changes"""
      if arguments:
        return "Encountered " + str(len(arguments)) + " arguments, expected 0"
      self.quitting = True
      return 'Now quitting'
  
  ###########
  
  def process_command(self):
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
    
  def print_status_line(self):
    self.status_line = " " + self.status + (" " * (self.cols - len(self.status) - 1))
    termcolor.cprint(self.status_line, attrs=['reverse'])
    
  def print_titlebar(self):
    modename = self.mode_names[self.mode]
    padsize = (self.cols-len(modename))/2
    padding = (" " * int(padsize))
    titlebar_string = padding + modename + padding
    if len(titlebar_string) < self.cols:
      titlebar_string += " "
    termcolor.cprint(titlebar_string, attrs=['reverse'])
    
  def vertical_pad(self):
    print("\n" * (self.lines-(self.used_lines+4)))
    
  def run(self):
    while not self.quitting:
      self.cols, self.lines = shutil.get_terminal_size()
      self.print_titlebar()
      self.used_lines = self.mode_content[self.mode]()
      self.vertical_pad()
      self.print_status_line()
      self.command, self.arguments = self.split_input(input("> "))
      self.process_command()
      #os.system("clear")
    