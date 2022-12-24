import time, subprocess, sys, os, argparse
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

def validateArgs():
    parser = argparse.ArgumentParser(description = 'Auto-encode downloaded ePub files to UTF-8')
    parser.add_argument('-p', '--path', required = True, dest = 'library_path', help = 'Path to Calibre library directory')
    args = parser.parse_args()
    library_path = args.library_path

    if not os.path.exists(library_path):
        sys.exit(f"{library_path} does not exist. Please double check your library path.")
    elif not os.path.exists(library_path + "/metadata.db"):
        sys.exit(f"Calibre library database file does not exists. Please double check your library path.")
    else:
        return library_path

def checkCalibreDebugInstallation():
    calibreDebugInfo = subprocess.run(['which', 'calibre-debug'], capture_output=True)
    if calibreDebugInfo.returncode != 0:
        sys.exit("calibre-debug not found. Is the Calibre Content Server installed?")
    else:
        return True

def on_created(event):
    print(f"\"{event.src_path}\" has been created. Calling Modify ePub CLI...")
    subprocess.run(["calibre-debug", "/root/modify_epub_plugin/commandline/me.py", "--", event.src_path, "--encode_html_utf8"])

def main():
    checkCalibreDebugInstallation()
    path = validateArgs()

    patterns = ["*.epub"]
    ignore_patterns = None
    ignore_directories = True
    case_sensitive = True

    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created

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
