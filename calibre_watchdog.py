import time, subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

def on_created(event):
    print(f"{event.src_path} has been created.")
    subprocess.run(["calibre-debug", "/root/modify_epub_plugin/commandline/me.py", "--", "--help"])

def main():
    patterns = ["*.epub"]
    ignore_patterns = None
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = on_created

    path = "."
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()

if __name__ == "__main__":
    main()
