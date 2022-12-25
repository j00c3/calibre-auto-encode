import time, subprocess, sys, os, argparse, logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

log_path = f"{os.getcwd()}/watchdog.log"
print(log_path)
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG, filename=log_path, filemode='a')

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
        logging.error("`which calibre-debug` failed. Calibre Content Server may not be installed")
        sys.exit(1)

def checkLibraryLocation(library_path):
    if not os.path.exists(library_path + "/metadata.db"):
        logging.error("Calibre library metadata database lookup failed.")
        sys.exit(f"Calibre library database file does not exist, or the library path is incorrect. Please double check your library path.")
    else:
        return True

def checkPluginInstallation(plugin_path):
    if not os.path.exists(plugin_path + "/commandline/me.py"):
        logging.error("Modify ePub plugin CLI tools lookup failed.")
        sys.exit("Modify ePub plugin commandline tool does not exist. Please double check your Modify ePub plugin path.\n\
            The plugin can be found at https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub")
    else:
        return True

def on_created(event):
    print(f"New file \"{event.src_path}\" has been created. Calling Modify ePub CLI...")
    process_output = subprocess.check_output(["calibre-debug", plugin_path + "/commandline/me.py", "--", event.src_path, "--encode_html_utf8"], text=True)
    if "BadZipfile" in process_output:
        logging.error(f"Modification of {event.src_path} failed. Not a valid ePub file.")
        print('Error: File is not a valid ePub file.')
    elif "FileNotFoundError" in process_output:
        logging.error(f"Modification of {event.src_path} failed. File may have been renamed.")
        print('Error: File not found; it may have been renamed.')
    else:
        logging.info(f"Successfully modified {event.src_path}.")
        print(process_output)
        
def main():
    logging.info('Watchdog started')
    calibre_library_path = validateArgs()

    patterns = ["*.epub"]
    ignore_patterns = None
    ignore_directories = True
    case_sensitive = True

    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created
    my_event_handler.on_moved = on_moved
    my_event_handler.on_modified = on_modified
    my_event_handler.on_any_event = on_any_event

    my_observer = Observer()
    my_observer.schedule(my_event_handler, calibre_library_path, recursive=True)

    my_observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('Watchdog shutting down...')
        my_observer.stop()
        my_observer.join()

if __name__ == "__main__":
    main()