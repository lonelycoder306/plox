# Opens a new console window with a Python shell.
# Works on Windows.
import subprocess
subprocess.Popen(['start', 'cmd', '/K', 'python'], shell=True)
# '/K python' keeps the new console window open after the command completes