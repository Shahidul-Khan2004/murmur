import argparse
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import shlex
from termcolor import colored
import os
import text_processing as tp
import image_selector
import image_viewer
import image_file_utils as ifu
from datetime import datetime
from qr import generate_qr_code_from_text, merge_qr_into_image

TITLE = R"""$$\      $$\ $$\   $$\ $$$$$$$\  $$\      $$\ $$\   $$\ $$$$$$$\  
$$$\    $$$ |$$ |  $$ |$$  __$$\ $$$\    $$$ |$$ |  $$ |$$  __$$\ 
$$$$\  $$$$ |$$ |  $$ |$$ |  $$ |$$$$\  $$$$ |$$ |  $$ |$$ |  $$ |
$$\$$\$$ $$ |$$ |  $$ |$$$$$$$  |$$\$$\$$ $$ |$$ |  $$ |$$$$$$$  |
$$ \$$$  $$ |$$ |  $$ |$$  __$$< $$ \$$$  $$ |$$ |  $$ |$$  __$$< 
$$ |\$  /$$ |$$ |  $$ |$$ |  $$ |$$ |\$  /$$ |$$ |  $$ |$$ |  $$ |
$$ | \_/ $$ |\$$$$$$  |$$ |  $$ |$$ | \_/ $$ |\$$$$$$  |$$ |  $$ |
\__|     \__| \______/ \__|  \__|\__|     \__| \______/ \__|  \__|
"""
POSTS_DIR = "posts"

def clear_console():
    """Clears the console screen universally."""
    # Check the operating system name
    if os.name == 'nt':
        # Command for Windows
        _ = os.system('cls')
    else:
        # Commands for Linux/macOS (posix)
        _ = os.system('clear')

class NoExitArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            format_help = "\n".join([l for l in message.splitlines() if not "usage:" in l and len(l.strip()) > 0])
            print(format_help)

@dataclass
class Input:
    arg_parser: NoExitArgumentParser
    def __init__(self):
        self.arg_parser = NoExitArgumentParser(description="Unvail your feelings, start typing a message", add_help=False)
        self.arg_parser.add_argument("--show", action='store_true', help="Shows recently posted image list...")
        #self.arg_parser.add_argument("--view", nargs=1, type=int, help="Select an image index to view.")
        self.arg_parser.add_argument("--clear", action='store_true', help="Clears the screen.")
        self.arg_parser.add_argument("--exit", action='store_true', help="Exits the program.")
        self.arg_parser.add_argument("--help", action='store_true', help="Help text printed.")

    def print_help(self):
        # Stripping off the usage line...
        print(colored(TITLE, 'green'))
        format_help = "\n".join([l for l in self.arg_parser.format_help().splitlines() if not "usage:" in l and len(l.strip()) > 0])
        print(format_help)

    def update(self) -> bool:
        user_input = input("> ").strip()
        if user_input.startswith("--"):
            args = self.arg_parser.parse_args(shlex.split(user_input))
            if args.help:
                self.print_help()
            elif args.exit:
                return False
            elif args.clear:
                clear_console()
            elif args.show:
                image_viewer.GridImageViewer(POSTS_DIR)
        elif len(user_input) > 0:
            while True:
                user_wants_img = input("Do you want to provide your own image path for your message feelings?((y)es/(N)o)").strip().lower()
                img_path = ""
                if user_wants_img == "y" or user_wants_img == "yes":
                    img_path = input("Provide path: ")
                else:
                    img_path = image_selector.select_image(tp.analyze_sentiment(user_input))
                
                qr_png = generate_qr_code_from_text(user_input)
                merged_png = merge_qr_into_image(qr_png, img_path)
                image_viewer.show_image(merged_png)

                user_wants_to_post = input("Do you want to post the image, or redo?((Y)es/(n)o/r(edo))").strip().lower()
                match user_wants_to_post:
                    case "y" | "yes" | "":
                        ifu.save_image_current_time(merged_png, POSTS_DIR)
                        break
                    case "n" | "no":
                        break
                    case "r" | "redo":
                        continue
                    case _:
                        logging.warning("Invalid choice starting over!")
                        break

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