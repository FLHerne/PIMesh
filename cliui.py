# Code by CEDStone, debated with and nitpicked by FLHerne
# User-interface for a general-purpose information-management tool

import shutil
import termcolor
import os
from enum import Enum


class UI:
  """A command-line user interface to the pimesh network backend"""
  Mode = Enum('Mode', ('list', 'links', 'help', 'duck'))
  mode_names = {
    Mode.list: "List of Entities",
    Mode.links: "Single Entity Links",
    Mode.help: "Documentation",
    Mode.duck: "Anatid"
  }
  

  def __init__(self, network):
    """This doesn't really need a docstring, does it?"""
    self.network = network
    self.quitting = False
    
    self.mode = self.Mode.list
    self.current_entity = None
    
    self.status = "Started PIMesh"
    self.titlebar = "PIMesh"
    self.cols, self.lines = shutil.get_terminal_size()
    
    self.used_lines = 0     # Used for vertical padding
    
    self.commands = {
      "duck": self.command_duck,
      "list": self.command_list,
      "view": self.command_view,
      "help": self.command_help,
      "add": self.command_add,
      "remove": self.command_remove,
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
      print((str(n).rjust(2) + " │ " + entity + "\t(" + str(len(self.network[entity])) + ")").expandtabs(5))
    self.titlebar = "Showing all entities"
    return len(self.network.targets)
  
  def links_print(self):	
    #print("links go here")
    for n, link in enumerate(self.network[self.current_entity]):
      print(str(n).rjust(2) + " │ " + link.tag + ": "+ link.target)
    number_of_links = len(self.network[self.current_entity])
    if number_of_links:
      self.titlebar = "Showing all links associated with '" + self.current_entity + "'"
    else:
      self.titlebar = "There are currently no links associated with '" + self.current_entity + "'"
    return number_of_links
  
  def help_print(self):
    """Display the docstrings for all commands"""
    for command in self.commands.items():
      termcolor.cprint(command[0], attrs=['bold'])
      print("  " + command[1].__doc__ + '\n')
    self.titlebar = "Showing documentation"
    return len(self.commands)*3
  
  def duck_print(self):
    """Draw an ASCII-art duck"""
    print("\n   >(')____, \n    (` =~~/  \n ~^~^`---'~^~^~")
    self.titlebar = "Showing wildfowl"
    return 4
      
  ### 
  
  def command_duck(self, mode, args):
    """Draw a duck"""
    if args:
        return self.args_error(len(args), "0")
    self.mode = self.Mode.duck
    return("Switched to duck mode")
  
  def command_list(self, mode, args):
    """Print a list of every entity involved in one of more links"""
    if args:
        return self.args_error(len(args), "0")
    self.mode = self.Mode.list
    return("Switched to entity list mode")
  
  def command_help(self, mode, args):
    """List and describe all commands"""
    if args:
        return self.args_error(len(args), "0")
    self.mode = self.Mode.help
    return("Switched to help mode")
  
  def command_view(self, mode, args):
    """View a specific entity. Note that you can refer to entities using thier index (line number)"""
    if len(args) != 1:
        return self.args_error(len(args), "1")
    try:
      try:
        if self.mode == self.Mode.links:
          self.current_entity = self.network[self.current_entity].targets[int(args[0])]
        else:
          self.current_entity = self.network.targets[int(args[0])]
      except IndexError:
        return "Could not switch to entity " + args[0] + " - index not in use"
    except ValueError:
      self.current_entity = args[0]
    self.mode = self.Mode.links
    return("Switched to showing links for '" + self.current_entity + "'")
  
  def command_remove(self, mode, args):
    """Remove a link from the current entity"""
    if len(args) not in range(2, 4):
      return self.args_error(len(args), "2 or 3")
    else:
      tag, target, *rest = args
      inverse_tag = rest[0] if rest else self.network.reciprocal(tag)
      try:
        self.network.unlink(self.current_entity, tag, target, inverse_tag)
        return 'Removed link "' + tag + ": " + target + '"'
      except ValueError:
        return 'No such link: "' + tag + ": " + target + '"'
      
  def command_add(self, mode, args):
    """Add a link from the current entity"""
    if len(args) not in range(2, 4):
      return self.args_error(len(args), "2 or 3")
    else:
      tag, target, *rest = args
      inverse_tag = rest[0] if rest else self.network.reciprocal(tag)
      try:
        self.network.addlink(self.current_entity, tag, target, inverse_tag)
        return 'Added link "' + tag + ": " + target + '"'
      except ValueError:
        return 'Error: Link "' + tag + ": " + target + '"already exists.'
  
  def command_quit(self, mode, args):
      """Trigger a clean exit from the program, saving changes"""
      if args:
        return self.args_error(len(args), "0")
      self.quitting = True
      return 'Now quitting'
  
  ###
  
  def pluralise(self, noun, number):
    if number == 1:
      return noun
    if noun[-1] == 's':
      return noun + "es"
    return noun + "s"
  
  def args_error(self, encountered, requirement):
    return "Encountered " + str(encountered) + " " + self.pluralise("arg", encountered) + ", expected " + requirement
  
  def process_command(self):
    """Choose which commnd to feed args to"""
    try:
      if False:
        self.args.append(str(int(self.command)))
        self.command = "view"
    except ValueError:
      pass
    try:
      self.status = self.commands[self.command](self.mode, self.args)
    except KeyError:
      self.status = "Unknown command: " + self.command
    
      
  def split_input(self, user_input):
    """Split user input into a command and a list of arguments"""
    command, *args = user_input.split(" ", 1)
    if len(args) > 0:
      args = args[0].split(":")
    args = [arg.strip() for arg in args]
    args = [arg for arg in args if arg]
    return command, args
    
  def print_status_line(self):
    """Draw the statusbar"""
    termcolor.cprint((" " + self.status).ljust(self.cols), attrs=['reverse'])
    
  def print_titlebar(self):
    """Draw titlebar to the terminal, and attempt to set the WM titlebar (if available)"""
    #modename = self.mode_names[self.mode]
    termcolor.cprint((" " + self.titlebar).ljust(self.cols), attrs=['reverse'])
    print("\x1B]0;%s\x07" % ("PIMesh: " + self.titlebar), end='')
    
  def vertical_pad(self):
    """Pad content to ensure statusbar and prompt are at bottom of display"""
    print("\n" * (self.lines-(self.used_lines+4)))
    
  def run(self):
    """Main loop, program spends most of its time in here"""
    while not self.quitting:
      self.cols, self.lines = shutil.get_terminal_size()
      self.used_lines = self.mode_content[self.mode]()
      self.vertical_pad()
      self.print_titlebar()
      self.print_status_line()
      self.command, self.args = self.split_input(input("> "))
      self.process_command()
      os.system("clear")
    