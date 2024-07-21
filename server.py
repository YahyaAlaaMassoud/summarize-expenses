import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.gradio_process = subprocess.Popen([
            'python', 'expenses.py'
        ])

    def on_modified(self, event):
        if event.src_path.endswith("expenses.py"):
            print(f"Detected changes in {event.src_path}. Restarting Gradio app...")
            self.gradio_process.kill()  # Stop the current process
            self.gradio_process = subprocess.Popen([
                'python', 'expenses.py'
            ])  # Start a new process

handler = ChangeHandler()
observer = Observer()
observer.schedule(handler, path='.', recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
