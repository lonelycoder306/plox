'''
import os
import sys

def clear_console():
    """Clears the console screen based on the operating system."""
    if sys.platform.startswith('win'):
        os.system('cls')  # Command for Windows
    else:
        os.system('clear') # Command for Linux/macOS

# Example usage:
print("This text will be cleared.")
input("Press Enter to clear the console...")
clear_console()
print("Console cleared!")
'''

import time

def clear_specific_text(text_to_clear, replacement_text=""):
    """
    Overwrites specific text on the console with a replacement text.
    If no replacement_text is provided, it effectively clears the text.
    """
    # Print the text to be cleared
    print(text_to_clear, end='\r') 
    # Overwrite with spaces or the replacement text
    print(replacement_text.ljust(len(text_to_clear)), end='\r')
    # Ensure the change is visible immediately
    import sys
    sys.stdout.flush()

print("This is some initial text.")
time.sleep(1) 
print("Counting down: 5")
time.sleep(1)
clear_specific_text("Counting down: 5", "Counting down: 4")
time.sleep(1)
clear_specific_text("Counting down: 4", "Counting down: 3")
time.sleep(1)
clear_specific_text("Counting down: 3", "Counting down: 2")
time.sleep(1)
clear_specific_text("Counting down: 2", "Counting down: 1")
time.sleep(1)
clear_specific_text("Counting down: 1", "Blast off!      ") # Add spaces to ensure full overwrite
print("\nProgram finished.")