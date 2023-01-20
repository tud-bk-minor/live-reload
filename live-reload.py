import subprocess
import pyinotify
import argparse

# First, set up a directory watcher for directory_to_watch
# Then, launch `python file_to_run` as a subprocess.
# Rerminate it and relaunch when any file 
# in the dir directory_to_watch is changed.
parser = argparse.ArgumentParser(
    prog='live-reload',
    description='Watch a directory (directory_to_watch) and relaunch a subprocess (of file_to_run) when any files in the directory are modified.',
    epilog='')
parser.add_argument('directory_to_watch')
parser.add_argument('file_to_run')
args = parser.parse_args()

# Launch the subprocess for the first time
process = subprocess.Popen(['python', args.file_to_run])

# Define a function to relaunch the subprocess, called by the event handler
def relaunch_subprocess():
    global process 
    global args
    new_process = None
    try:
        new_process = subprocess.Popen(['python', args.file_to_run])
    except:
        print('Failed to relaunch subprocess.')
        return
    process.kill()
    process = new_process

# Define a handler for the events
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        relaunch_subprocess()
        
    def process_IN_DELETE(self, event):
        relaunch_subprocess()

    def process_IN_MODIFY(self, event):
        relaunch_subprocess()


watch_manager = pyinotify.WatchManager()
mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY  # watched events

handler = EventHandler()
notifier = pyinotify.Notifier(watch_manager, handler)
# Watch the directory_to_watch but ignore __pycache__ subdirectories 
wdd = watch_manager.add_watch(args.directory_to_watch, mask, rec=True, exclude_filter=lambda x: x.endswith('__pycache__'))

# Start the notifier loop
notifier.loop();
