import time, subprocess, sys, argparse, logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import LoggingEventHandler
<<<<<<< Updated upstream
=======

# set your own log path and name
log_path = "watchdog.log"
>>>>>>> Stashed changes

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG, filename=log_path, filemode='a')

def validateArgs():
<<<<<<< Updated upstream
    parser = argparse.ArgumentParser(description = 'Auto-encode downloaded ePub files to UTF-8')
=======
    parser = argparse.ArgumentParser(description = 'Auto-encode downloaded ePub files to UTF-8 then import to Calibre library')
>>>>>>> Stashed changes
    parser.add_argument('-d', '--download', required = True, dest = 'download_path', help = 'Path to Sabnzbd books download directory')
    parser.add_argument('-l', '--library', required = True, dest = 'library_path', help = 'Path to Calibre library directory')
    parser.add_argument('-p', '--plugin', required = True, dest = 'plugin_path', help = 'Path to Modify ePub plugin directory')
    args = parser.parse_args()
    global plugin_path, download_path, library_path
    download_path = args.download_path
    library_path = args.library_path
    plugin_path = args.plugin_path

    checkCalibreDebugInstallation()
    checkPaths(download_path, library_path)
    checkPluginInstallation(plugin_path)

    return download_path

def checkCalibreDebugInstallation():
    try:
        subprocess.check_output(['which', 'calibre-debug'])
    except subprocess.CalledProcessError as e:
        print("calibre-debug not found. Is the Calibre Content Server installed?")
        logging.error("`which calibre-debug` failed. Calibre Content Server may not be installed")
        sys.exit(1)

def checkPaths(download_path, library_path):
    if not os.path.exists(library_path + "/metadata.db"):
        logging.error("Library folder does not exist")
        sys.exit(f"Library path does not exist, or the path is incorrect. Please double check your parameter.")
    elif not os.path.exists(download_path):
        logging.error("Download folder does not exist")
        sys.exit(f"Download path does not exist, or the path is incorrect. Please double check your parameter.")
    else:
        return True

def checkPluginInstallation(plugin_path):
    if not os.path.exists(plugin_path + "/commandline/me.py"):
        logging.error("Modify ePub plugin CLI tools lookup failed")
        sys.exit("Modify ePub plugin commandline tool does not exist. Please double check your Modify ePub plugin path.\n\
            The plugin can be found at https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub")
    else:
        return True

def on_created(event):
    print(f"New ePub file \"{event.src_path}\" detected. Calling Modify ePub CLI...")
    modify_process_output = subprocess.check_output(["calibre-debug", plugin_path + "/commandline/me.py", "--", event.src_path, "--encode_html_utf8"], text=True)
<<<<<<< Updated upstream
    if "BadZipfile" in modify_process_output: 
=======
    if "BadZipfile" in modify_process_output:
>>>>>>> Stashed changes
        logging.error(f"Modification of {event.src_path} failed. Not a valid ePub file")
        print('Error: File is not a valid ePub file')
        return
    elif "FileNotFoundError" in modify_process_output:
        logging.error(f"Modification of {event.src_path} failed. File may have been renamed or moved")
        print('Error: File not found; it may have been renamed or moved')
        return
    elif "not changed" in modify_process_output:
        logging.info(f"{event.src_path} not modified. Looks like it was already UTF-8 encoded")
    else:
        print(modify_process_output)
        logging.info(f"Successfully modified {event.src_path}. Importing to Calibre library...")
        import_process_output = subprocess.check_output(["calibredb", "add", f"--with-library={library_path}", event.src_path], text=True)
        if "Added" in import_process_output:
            print(import_process_output)
            logging.info(f"Successfully imported {event.src_path} into to Calibre library")
        else:
            logging.warning(import_process_output)

def main():
    logging.info('Watchdog started')
    validateArgs()

    patterns = ["*.epub"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True

    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created

    my_observer = Observer()
    my_observer.schedule(my_event_handler, download_path, recursive=True)
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