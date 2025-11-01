#!/usr/bin/env python3
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BuildHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and (event.src_path.endswith('.yaml') or event.src_path.endswith('.yml')):
            print("🔄 File changed, rebuilding...")
            os.system("python3 build.py")
            print("✅ Rebuild complete!")

    def on_created(self, event):
        if not event.is_directory and (event.src_path.endswith('.yaml') or event.src_path.endswith('.yml')):
            print("🆕 New file created, rebuilding...")
            os.system("python3 build.py")
            print("✅ Rebuild complete!")

    def on_deleted(self, event):
        if not event.is_directory and (event.src_path.endswith('.yaml') or event.src_path.endswith('.yml')):
            print("🗑️ File deleted, rebuilding...")
            os.system("python3 build.py")
            print("✅ Rebuild complete!")

def main():
    print("👀 Watching src/ directory for changes... Press Ctrl+C to stop.")
    # Initial build
    print("🚀 Initial build...")
    os.system("python3 build.py")
    print("✅ Initial build complete!")

    observer = Observer()
    observer.schedule(BuildHandler(), path='src', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping watch...")
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()