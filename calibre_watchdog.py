import time, subprocess, sys, os, argparse
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

def validateArgs():
    parser = argparse.ArgumentParser(description = 'Auto-encode downloaded ePub files to UTF-8')
    parser.add_argument('-l', '--library', required = True, dest = 'library_path', help = 'Path to Calibre library directory')
    parser.add_argument('-p', '--plugin', required = True, dest = 'plugin_path', help = 'Path to Modify ePub plugin directory')
    args = parser.parse_args()
    library_path = args.library_path
    global plugin_path
    plugin_path = args.plugin_path

    checkCalibreDebugInstallation()
    checkLibraryLocation(library_path)
    checkPluginInstallation(plugin_path)

    return library_path

def checkCalibreDebugInstallation():
    try:
        subprocess.check_output(['which', 'calibre-debug'])
    except subprocess.CalledProcessError as e:
        print("calibre-debug not found. Is the Calibre Content Server installed?")
        sys.exit(1)

def checkLibraryLocation(library_path):
    if not os.path.exists(library_path):
        sys.exit(f"{library_path} does not exist. Please double check your library path.")
    elif not os.path.exists(library_path + "/metadata.db"):
        sys.exit(f"Calibre library database file does not exists. Please double check your library path.")
    else:
        return True

def checkPluginInstallation(plugin_path):
    if not os.path.exists(plugin_path + "/commandline/me.py"):
        sys.exit("Modify ePub plugin commandline tool does not exist. Please double check your Modify ePub plugin path.\n\
            The plugin can be found at https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub")
    else:
        return True

def on_created(event):
    print(f"New file \"{event.src_path}\" has been created. Calling Modify ePub CLI...")
    process_output = subprocess.check_output(["calibre-debug", plugin_path + "/commandline/me.py", "--", event.src_path, "--encode_html_utf8"], text=True)
    if "BadZipfile" in process_output:
        print('File is not a valid ePub file!')
    else:
        print(process_output)

def main():    
    calibre_library_path = validateArgs()

    patterns = ["*.epub"]
    ignore_patterns = None
    ignore_directories = True
    case_sensitive = True

    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created

    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, calibre_library_path, recursive=go_recursively)

    my_observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()

if __name__ == "__main__":
    main()