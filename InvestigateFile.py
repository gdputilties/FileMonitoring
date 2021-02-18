import csv
import os
import re

from jproperties import Properties

import RecordDetails
import SendEmailNotification




def read_csv_file(file_path):
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                line_count += 1
        print(f'Processed {line_count} lines.')


def is_valid_line_to_iterate(line):
    date_pattern = "^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])*"
    result = re.search(date_pattern, line)
    if result:
        return True
    else:
        return False


def read_log_file(file_path, event_type):
    old_logs_cleared = False
    proceed_to_next_line = False
    file1 = open(file_path, 'r')
    lines = file1.readlines()
    count = 0
    last_line = ""
    error_type = get_value_from_properties_file_by_key("ErrorType")
    errors_types = error_type.split(",")
    # print("errArr :", errors_types)
    last_ran_time = RecordDetails.log_last_running_time
    # Strips the newline character
    err_line_count = 0
    print("Checking for errors in the lines ")
    for line in lines:
        valid_line = is_valid_line_to_iterate(line)
        if not valid_line:
            print(line, " is not valid line")
            continue
        # print(line)
        if not proceed_to_next_line:
            if last_ran_time != "":
                if not line.startswith(last_ran_time):
                    continue
                elif not proceed_to_next_line:
                    proceed_to_next_line = True
                    continue
            else:
                proceed_to_next_line = True
        if proceed_to_next_line:
            for err_type in errors_types:
                if err_type in line:
                    # print(err_type + " is in ", line)
                    err_line_count = err_line_count + 1
                    # print("err_date: ",err_date)
                    if err_line_count >= 3:
                        err_date = line[0:27]
                        if event_type == "created":
                            if not old_logs_cleared:
                                delete_old_logs_from_record_errors_file(file_path)
                                old_logs_cleared=True

                        # Recording errors to RecordErrors.txt file
                        record_errors(line)
                        SendEmailNotification.notify_errors(file_path, event_type, err_date, line);
                    last_ran_time = ""

        # print("Line{}: {}".format(count, line.strip()))
        last_line = line
    if last_line != "":
        RecordDetails.log_last_running_time = last_line[0:27]
        err_line_count = 0

    file1.close()


def get_value_from_properties_file_by_key(attr_type):
    configs = Properties()
    with open('SystemProperties.properties', 'rb') as read_prop:
        configs.load(read_prop)
        prop_view = configs.items()
        # print(type(prop_view))
        for item in prop_view:
            # print(item)
            if item[0] == attr_type:
                return item[1][0]


def delete_old_logs_from_record_errors_file(file_path):
    """In a file, delete the lines at line number in given list"""
    # Create name of dummy / temporary file
    original_file = "RecordErrors.txt"
    dummy_file = original_file + '.bak'
    # Open original file in read only mode and dummy file in write mode
    write_obj = open(dummy_file, "w")
    write_obj.write("Error logs generated for the file " + file_path)
    write_obj.write("\n")
    write_obj.close()
    os.remove(original_file)
    os.rename(dummy_file, original_file)


def record_errors(log_error):
    f = open("RecordErrors.txt", "a")
    f.write(log_error)
    f.close()

# print(get_value_from_properties("WatchDIR"))
# line = input("enter line")
# print("matched ", is_valid_line_to_iterate(line))
