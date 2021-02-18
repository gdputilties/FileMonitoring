import os
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import InvestigateFile
import RecordDetails


def get_file_extension(file_name):
    file_tup = os.path.splitext(file_name)
    return file_tup[1]


def get_file_name(src_path, wachdirectory):
    len_watch_dir_path = len(wachdirectory)
    len_event_src_path = len(src_path)
    watch_file = src_path[len_watch_dir_path:len_event_src_path]
    return watch_file


# Creating class MyHandler which extends FileSystemEventHandler(Watchdog api class)
class MyHandler(FileSystemEventHandler):
    # Fetching watch folder from property file.
    watchDirectory = InvestigateFile.get_value_from_properties_file_by_key("WatchDIR")
    # Below we are sorting the files by modified date
    sorted(Path(watchDirectory).iterdir(), key=os.path.getmtime, reverse=True)

    # Overriding methods from FileSystemEventHandler class on_modified and on_created
    def on_modified(self, event):
        file_path = event.src_path
        event_type = event.event_type
        # getting below last modified date and time
        # modified_date = time.ctime(os.path.getmtime(file_path))
        # print(file_path, " is ", event_type, " on ", modified_date)
        file_name = get_file_name(file_path, self.watchDirectory)
        fileStartsWith = InvestigateFile.get_value_from_properties_file_by_key("FileStartsWith")
        if file_name.startswith(fileStartsWith):
            print(file_name, " is ", event_type)
            InvestigateFile.read_log_file(file_path, event_type)

    def on_created(self, event):
        event_type = event.event_type
        file_path = event.src_path
        # getting created date time
        # create_date = time.ctime(os.path.getctime(event.src_path))
        # print(file_path, " is ", event_type, " on ", create_date)
        file_name = get_file_name(file_path, self.watchDirectory)
        # file_extension = get_file_extension(file_name)
        fileStartsWith = InvestigateFile.get_value_from_properties_file_by_key("FileStartsWith")
        if file_name.startswith(fileStartsWith):
            if RecordDetails.last_ran_file_name == file_name:
                event_type = "modified"
            else:
                RecordDetails.log_last_running_time = ""
            print(file_name, " is ", event_type)
            InvestigateFile.read_log_file(file_path, event_type)
            RecordDetails.last_ran_file_name = file_name


event_handler = MyHandler()
observer = Observer()
path = InvestigateFile.get_value_from_properties_file_by_key("WatchDIR")
observer.schedule(event_handler, path, recursive=False)
observer.start()
try:
    print("Started Monitoring Folder:", path)
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
