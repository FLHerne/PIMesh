import shutil
import termcolor
import os
from enum import Enum


class UI:
  Mode = Enum('Mode', ('list', 'links', 'help', 'duck'))
  mode_names = {
    Mode.list: "Entity List",
    Mode.links: "Single entity view",
    Mode.help: "Documentation",
    Mode.duck: "Anatid Display"
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
      "quit": self.command_quit,
      "exit": self.command_quit
    }
    
    self.mode_content = {
      UI.Mode.list: self.list_print,
      UI.Mode.links: self.links_print,
      UI.Mode.help: self.help_print,
      UI.Mode.duck: self.duck_print
    }
      
  def list_print(self):	
    print("list goes here")
    return 1
  
  def help_print(self):	
    print("help goes here")
    return 1
  
  def links_print(self):	
    print("links go here")
    return 1
  
  def duck_print(self):	
    print("\n   >(')____, \n    (` =~~/  \n ~^~^`---'~^~^~")
    return 4
      
  ###########
  def command_duck(self, mode, arguments):
    """Draw a duck"""
    self.mode = self.Mode.duck
    return("Quack!")
  
  def command_list(self, mode, arguments):
    """Draw a duck"""
    self.mode = self.Mode.list
    return("Now entering list mode")
  
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
      self.used_lines = self.mode_content[self.mode]()  #FIXME
      self.vertical_pad()
      self.print_status_line()
      self.command, self.arguments = self.split_input(input("> "))
      self.process_command()
      #os.system("clear")
    