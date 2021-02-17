import csv
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
    proceed_next_line = False
    file1 = open(file_path, 'r')
    lines = file1.readlines()
    count = 0
    last_line = ""
    error_type = get_value_from_properties("ErrorType")
    errors_types = error_type.split(",")
    # print("errArr :", errors_types)
    last_ran_time = RecordDetails.log_last_running_time
    # Strips the newline character
    err_line_count = 0
    for line in lines:
        is_valid_line = is_valid_line_to_iterate(line)
        if not is_valid_line:
            print(line, " is not valid line")
            continue
        # print(line)
        if not proceed_next_line:
            if last_ran_time != "":
                if not line.startswith(last_ran_time):
                    continue
                elif not proceed_next_line:
                    proceed_next_line = True
                    continue
            else:
                proceed_next_line = True
        if proceed_next_line:
            for err_type in errors_types:
                if err_type in line:
                    # print(err_type + " is in ", line)
                    err_line_count = err_line_count + 1
                    err_date = line[0:27]
                    # print("err_date: ",err_date)
                    if err_line_count >= 3:
                        SendEmailNotification.update_log(file_path, event_type, err_date, line)
                        SendEmailNotification.notify_errors(file_path, event_type, err_date, line);
                    last_ran_time = ""

        # print("Line{}: {}".format(count, line.strip()))
        last_line = line
    if last_line != "":
        RecordDetails.log_last_running_time = last_line[0:27]
        err_line_count = 0

    file1.close()


def get_value_from_properties(attr_type):
    configs = Properties()
    with open('SystemProperties.properties', 'rb') as read_prop:
        configs.load(read_prop)
        prop_view = configs.items()
        # print(type(prop_view))
        for item in prop_view:
            # print(item)
            if item[0] == attr_type:
                return item[1][0]


# print(get_value_from_properties("WatchDIR"))
# line = input("enter line")
# print("matched ", is_valid_line_to_iterate(line))
