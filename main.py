import argparse
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import shlex
from termcolor import colored
import os

TITLE = R"""$$\      $$\ $$\   $$\ $$$$$$$\  $$\      $$\ $$\   $$\ $$$$$$$\  
$$$\    $$$ |$$ |  $$ |$$  __$$\ $$$\    $$$ |$$ |  $$ |$$  __$$\ 
$$$$\  $$$$ |$$ |  $$ |$$ |  $$ |$$$$\  $$$$ |$$ |  $$ |$$ |  $$ |
$$\$$\$$ $$ |$$ |  $$ |$$$$$$$  |$$\$$\$$ $$ |$$ |  $$ |$$$$$$$  |
$$ \$$$  $$ |$$ |  $$ |$$  __$$< $$ \$$$  $$ |$$ |  $$ |$$  __$$< 
$$ |\$  /$$ |$$ |  $$ |$$ |  $$ |$$ |\$  /$$ |$$ |  $$ |$$ |  $$ |
$$ | \_/ $$ |\$$$$$$  |$$ |  $$ |$$ | \_/ $$ |\$$$$$$  |$$ |  $$ |
\__|     \__| \______/ \__|  \__|\__|     \__| \______/ \__|  \__|
"""

def clear_console():
    """Clears the console screen universally."""
    # Check the operating system name
    if os.name == 'nt':
        # Command for Windows
        _ = os.system('cls')
    else:
        # Commands for Linux/macOS (posix)
        _ = os.system('clear')

@dataclass
class Input:
    arg_parser: argparse.ArgumentParser
    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(description="Unvail your feelings, start typing a message", add_help=False)
        self.arg_parser.add_argument("--show", action='store_true', help="Shows recently posted image list...")
        self.arg_parser.add_argument("--view", nargs=1, type=int, help="Select an image index to view.")
        self.arg_parser.add_argument("--clear", action='store_true', help="Clears the screen.")
        self.arg_parser.add_argument("--exit", action='store_true', help="Exits the program.")
        self.arg_parser.add_argument("--help", action='store_true', help="Help text printed.")

    def print_help(self):
        # Stripping off the usage line...
        print(colored(TITLE, 'green'))
        format_help = "\n".join([l for l in self.arg_parser.format_help().splitlines() if not "usage:" in l and len(l.strip()) > 0])
        print(format_help)

    def update(self) -> bool:
        user_input = input("> ")
        args = self.arg_parser.parse_args(shlex.split(user_input))
        #print(args)
        if args.help:
            self.print_help()
        elif args.exit:
            return False
        elif args.clear:
            clear_console()
        elif len(user_input.strip()) > 0:
            pass
        return True

def main():
    user_input = Input()
    user_input.print_help()
    while True:
        try:
           if not user_input.update():
               break
        except Exception as e:
            logging.error(colored(e, 'red'))

if __name__ == "__main__":
    main()