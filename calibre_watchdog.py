import time, subprocess, sys, os, argparse, logging, shutil
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# set your own log path and name
log_path = "watchdog.log"

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG, filename=log_path, filemode='a')

def validate_args():
    parser = argparse.ArgumentParser(description = 'Auto-encode downloaded ePub files to UTF-8 then import to Calibre library')
    parser.add_argument('-d', '--download-path', required=True, dest='download_path', help='Path to Sabnzbd books download directory')
    parser.add_argument('-l', '--library-path', required=True, dest='library_path', help='Path to Calibre library directory')
    parser.add_argument('-p', '--plugin-path', required=True, dest='plugin_path', help='Path to Modify ePub plugin directory')
    parser.add_argument('--delete_completed', action=argparse.BooleanOptionalAction, default=False, help='Delete the directory of newly downloaded book if UTF-8 conversion and Calibre import are successful')
    args = parser.parse_args()
    global delete_completed
    delete_completed = args.delete_completed
    global plugin_path, library_path
    download_path = args.download_path
    library_path = args.library_path
    plugin_path = args.plugin_path

    check_calibre_installation()
    check_paths(download_path, library_path)
    check_plugin_installation(plugin_path)

    return download_path

def check_calibre_installation():
    try:
        subprocess.check_output(['which', 'calibre-debug'])
    except subprocess.CalledProcessError as e:
        print("calibre-debug not found. Is the Calibre Content Server installed?")
        logging.error("`which calibre-debug` failed. Calibre Content Server may not be installed")
        sys.exit(1)

def check_paths(download_path, library_path):
    if not os.path.exists(library_path + "/metadata.db"):
        logging.error("Library folder does not exist")
        sys.exit(f"Library path does not exist, or the path is incorrect. Please double check your parameter.")
    elif not os.path.exists(download_path):
        logging.error("Download folder does not exist")
        sys.exit(f"Download path does not exist, or the path is incorrect. Please double check your parameter.")
    else:
        return True

def check_plugin_installation(plugin_path):
    if not os.path.exists(plugin_path + "/commandline/me.py"):
        logging.error("Modify ePub plugin CLI tools lookup failed")
        sys.exit("Modify ePub plugin commandline tool does not exist. Please double check your Modify ePub plugin path.\n\
            The plugin can be found at https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub")
    else:
        return True

def on_created(event):
    modify_process_output = subprocess.check_output(["calibre-debug", plugin_path + "/commandline/me.py", "--", event.src_path, "--encode_html_utf8"], text=True)
    if "BadZipfile" in modify_process_output:
        logging.error(f"Modification of \"{event.src_path}\" failed. Not a valid ePub file")
        return
    elif "FileNotFoundError" in modify_process_output:
        logging.error(f"Modification of \"{event.src_path}\" failed. File may have been renamed or moved")
        return
    elif "not changed" in modify_process_output:
        logging.info(f"\"{event.src_path}\" not modified. Looks like it was already UTF-8 encoded")
        import_epub_to_calibre(event.src_path)
    else:
        logging.info(f"Successfully modified \"{event.src_path}\". Importing to Calibre library...")
        import_epub_to_calibre(event.src_path)

def import_epub_to_calibre(new_book_path):
    import_process_output = subprocess.check_output(["calibredb", "add", f"--with-library={library_path}", new_book_path], text=True)
    if "Added" in import_process_output:
        logging.info(f"Successfully imported \"{new_book_path}\" into to Calibre library.")
        if delete_completed:
            delete_successful_imports(new_book_path)
    else:
        logging.warning(import_process_output)

def delete_successful_imports(new_book_path):
    new_book_path_array = new_book_path.split('/')
    new_book_path_array.pop()
    new_book_parent_dir = "/".join(new_book_path_array)
    logging.info(f"Deleting \"{new_book_parent_dir}\" from the download folder...")
    try:
        shutil.rmtree(new_book_parent_dir)
        logging.info(f"Successfully deleted \"{new_book_parent_dir}\"")
    except:
        logging.error(f"Unable to delete \"{new_book_parent_dir}\"...")

def main():
    logging.info('Watchdog started')
    download_path = validate_args()

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