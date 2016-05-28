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
    self.current_entity = None
    
    self.status = "Started PIMesh"
    self.titlebar = "PIMesh"
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
    """Print a list of every entity involved in one or more links"""
    for n,entity in enumerate(self.network.targets):
      print(str(n) + " | " + entity)
    self.titlebar = "Showing all entities"
    return len(self.network.targets)
  
  def links_print(self):	
    #print("links go here")
    for n, link in enumerate(self.network[self.current_entity]):
      print(str(n) + " | " + link.tag + ": "+ link.target)
    number_of_links = len(self.network[self.current_entity])
    if number_of_links:
      self.titlebar = "Showing all links associated with [" + self.current_entity + "]"
    else:
      self.titlebar = "There are currently no links associated with [" + self.current_entity + "]"
    return number_of_links
  
  def help_print(self):
    """Display the docstrings for all commands"""
    for command in self.commands.items():
      termcolor.cprint(command[0], attrs=['bold'])
      print("  " + command[1].__doc__ + '\n')
    self.titlebar = "Showing documentation"
    return len(self.commands)*3
  
  def duck_print(self):	
    print("\n   >(')____, \n    (` =~~/  \n ~^~^`---'~^~^~")
    self.titlebar = "Showing wildfowl"
    return 4
      
  ###########
  def command_duck(self, mode, arguments):
    """Draw a duck"""
    if arguments:
        return "Encountered " + str(len(arguments)) + " argument(s), expected 0"
    self.mode = self.Mode.duck
    return("Switched to  duck mode")
  
  def command_list(self, mode, arguments):
    """Print a list of every entity involved in one of more links"""
    if arguments:
        return "Encountered " + str(len(arguments)) + " argument(s), expected 0"
    self.mode = self.Mode.list
    return("Switched to entity List mode")
  
  def command_help(self, mode, arguments):
    """List and describe all commands"""
    if arguments:
        return "Encountered " + str(len(arguments)) + " argument(s), expected 0"
    self.mode = self.Mode.help
    return("Switched to help mode")
  
  def command_view(self, mode, arguments):
    """View a specific entity"""
    if len(arguments) != 1:
      return "Error: Found " + str(len(arguments)) + " argument(s) - expected 1"
    try:
      try:
        if self.mode == self.Mode.links:
          self.current_entity = self.network[self.current_entity].targets[int(arguments[0])]
        else:
          self.current_entity = self.network.targets[int(arguments[0])]
      except IndexError:
        return "Could not switch to entity " + arguments[0] + " - index not in use"
    except ValueError:
      self.current_entity = arguments[0]
    self.mode = self.Mode.links
    return("Switched to showing links for [" + self.current_entity + "]")
  
  def command_quit(self, mode, arguments):
      """Trigger a clean exit from the program, saving changes"""
      if arguments:
        return "Encountered " + str(len(arguments)) + " argument(s), expected 0"
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
    
  def set_titlebar(self):
    modename = self.mode_names[self.mode]
    #self.titlebar = modename
    #padsize = (self.cols-len(self.titlebar))/2
    #padding = (" " * int(padsize))
    #titlebar_string = padding + self.titlebar + padding
    #if len(titlebar_string) < self.cols:
    #  titlebar_string += " "
    #termcolor.cprint(titlebar_string, attrs=['reverse'])
    termcolor.cprint((" " + self.titlebar + (" " * (self.cols - len(self.titlebar) - 1))), attrs=['reverse'])
    print("\x1B]0;%s\x07" % ("PIMesh: " + self.titlebar), end='')
    
  def vertical_pad(self):
    print("\n" * (self.lines-(self.used_lines+4)))
    
  def run(self):
    while not self.quitting:
      self.cols, self.lines = shutil.get_terminal_size()
      self.used_lines = self.mode_content[self.mode]()
      self.vertical_pad()
      self.set_titlebar()
      self.print_status_line()
      self.command, self.arguments = self.split_input(input("> "))
      self.process_command()
      os.system("clear")
    