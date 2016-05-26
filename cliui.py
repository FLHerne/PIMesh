import shutil
import termcolor
import os
from enum import Enum


class UI:
  Mode = Enum('Mode', ('list', 'links', 'help'))
  mode_names = {
    Mode.list: "Entity List",
    Mode.links: "Single entity view",
    Mode.help: "Documentation"
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
      "quit": self.command_quit,
      "exit": self.command_quit
    }
      
      
  ###########
  def command_duck(self, mode, arguments):
    print("\n   >(')____, \n    (` =~~/  \n ~^~^`---'~^~^~")
    self.used_lines = 4
    return("Quack!")
  
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
    
  def vertical_pad(self):
    print("\n" * (self.lines-(self.used_lines+3)))
    
  def run(self):
    while not self.quitting:
      self.cols, self.lines = shutil.get_terminal_size()
      self.vertical_pad()
      self.print_status_line()
      self.command, self.arguments = self.split_input(input("> "))
      self.process_command()
      #os.system("clear")
    