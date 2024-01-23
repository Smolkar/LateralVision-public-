"""This script provides functionality to convert a CSV file to JSON, process and format JSON data, 
filter and sort JSON data based on specified criteria.

Functions:
convert_csv_to_json(file_name): Converts a CSV file to JSON format.
format(data): Processes and formats JSON data.
create_valid_json(file_name): Reads in a file containing JSON data and returns a list of valid JSON objects.
convert_to_iso_date(date_string): Converts a date string to ISO format.
get_fresh(file_name, date, word_to_filter): Filters JSON data based on specified criteria.
get_domains(file_name): Extracts domain data from JSON file and prints domain name and events.
sort_json(file_name): Sorts JSON data based on specified criteria.
main(): Main function to run the script.
"""


import csv
import json
import os
from datetime import datetime

filtered_file = "filtered.json"
fixed_file = "event_log_fixed.json"

def convert_csv_to_json(file_name):
    """
    > We open the CSV file, read it, and then write it to a JSON file

    :param file_name: The name of the CSV file to be converted
    return: JSON

    """

    columns = [
        "EventTime",
        "Computer",
        "Channel",
        "EventID",
        "DomainName",
        "UserName",
        "LogonType",
        "SourceIP",
        "Description",
        "Message",
        "EventRecordID",
        "FullPath",
        "FlowId",
        "ClientId",
        "Fqdn",
    ]

    with open(file_name, "r") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    # with open("Data/data.json", "w") as f:
    #     json.dump(
    #
    #     )
    return json.dump(
        [{column: row[column] for column in columns} for row in data], f, indent=4
    )


def format(data):
    """
    It takes a JSON file, parses it, and then returns a list of dictionaries

    :param data: The data to be formatted
    :return: A list of dictionaries.
    """
    # with open(file_name) as f:
    #     data = json.load(f)
    #     f.close()

    for event in data:
        if event.get("Channel") not in [
            "Microsoft-Windows-PowerShell/Operational",
            "Microsoft-Windows-Time-Service/Operationa",
            "Microsoft-Windows-Diagnosis-Scripted/Operational",
            "Windows PowerShell",
        ]:
            if "Message" in event:
                message_lines = event["Message"].split("\n")
                message_dict = {}
                for line in message_lines:
                    key_value = line.split(":")
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()

                        # Remove trailing '\r', '\n', and '\'
                        if value.endswith("\\"):
                            value = value[:-1]
                        if value.endswith("\\r"):
                            value = value[:-2]
                        if value.endswith("\\n"):
                            value = value[:-2]

                        message_dict[key] = value
                event["Message"] = message_dict
        else:
            print(event.get("Channel"))

    return data
    # write the fixed JSON file
    # with open("event_log_fixed.json", "w") as f:
    #     f.write(json.dumps(data, indent=4))


def create_valid_json(file_name):
    """
    It reads in a file, converts each line to a Python dictionary, and then appends the dictionary to a
    list

    :param file_name: The name of the file to read
    :return: A list of dictionaries
    """
    data = []
    with open(file_name, "r") as f:
        for line in f:
            # Convert the line (which should be a JSON string) to a Python dictionary
            d = json.loads(line.strip())

            # Append the dictionary to the list
            data.append(d)
    f.close()
    return data


def convert_to_iso_date(date_string):
    """
    If the date string is in the format of YYYY-MM-DD, return it as is. If it's in the format of MM-DD,
    add the current year to it and return it

    :param date_string: The date string to be converted to ISO format
    :return: A string in the format of YYYY-MM-DDT00:00:00Z
    """
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        # If the date string is in the format of MM-DD, add the current year to it
        current_year = datetime.now().year
        date_string_with_year = f"{current_year}-{date_string}"
        date = datetime.strptime(date_string_with_year, "%Y-%m-%d")
    iso_date = date.strftime("%Y-%m-%dT00:00:00Z")
    return iso_date


def get_fresh(file_name, date, word_to_filter):
    """
    > It opens the file, reads the data, filters the data, and writes the filtered data to a new file

    :param file_name: the name of the file you want to filter
    :param date: The date you want to filter from
    :param word_to_filter: This is the word that you want to filter out
    """
    with open(file_name) as f:
        data = f.read()
        f.close()
    filtered_data = [
        obj
        for obj in data
        if obj["EventTime"] >= convert_to_iso_date(date)  # type: ignore
        and word_to_filter not in str(obj)
    ]

    with open(filtered_file, "w") as f:
        json.dump(filtered_data, f)


def get_domains(file_name):
    """
    It reads in a JSON file, counts the number of times each domain appears, and then removes any
    domains that only have events 1149 and 4624

    :param file_name: The name of the file you want to parse
    """
    with open(file_name) as f:
        data = json.loads(f.read())
        f.close()
    domains = {}
    events = {}
    for domain in data:
        domainname = domain["DomainName"].upper()
        event = domain["EventID"]
        domains[domainname] = domains.get(domainname, 0) + 1
        if domainname not in events:
            events[domainname] = {}
        events[domainname][event] = events[domainname].get(event, 0) + 1
    # remove domains with only events 1149 and 4624
    for domain in list(domains.keys()):
        if (
            len(events[domain]) == 2
            and 1149 in events[domain]
            and 4624 in events[domain]
        ):
            del domains[domain]

        # print(f"Domain: {domain}")
        # print(f"Events: {events[domain]}")


# function to sort the json objects by Fqdn after that bt EventRecordID
def sort_json(file_name):
    """
    It opens the file, reads the data, closes the file, sorts the data, opens the file again, writes the
    data, and closes the file

    :param file_name: The name of the file you want to sort
    """
    with open(file_name) as f:
        data = json.loads(f.read())
        f.close()
    data.sort(key=lambda x: (x["Fqdn"], x["EventRecordID"]))
    with open(filtered_file, "w") as f:
        json.dump(data, f)


# main function to run the script
def main():
    """
    It's a menu that allows the user to convert a CSV file to JSON, process a JSON file, or filter a
    JSON file
    """
    print(asci)

    while True:
        print("=================================")
        print("|           MAIN MENU           |")
        print("=================================")
        print("| 1. Convert CSV to JSON        |")
        print("| 2. Process JSON               |")
        print("| 3. Filter Data                |")
        print("| 5. Exit                       |")
        print("=================================")

        choice = input("Enter your choice (1-4): ")
        if choice == "1":
            file_name = input("Enter the name of the CSV file: ")
            try:
                convert_csv_to_json(file_name)
            except FileNotFoundError:
                # list the files in the current directory
                print("File not found. Please check the file name and try again.")
                print("Files in the current directory:")
                # print(os.listdir())
                continue

        elif choice == "2":
            file_name = input("Enter the name of the JSON file: ")
            try:
                try:
                    processed_json_one = create_valid_json(file_name)
                    processed_json = format(processed_json_one)

                except json.decoder.JSONDecodeError:
                    with open(file_name) as f:
                        data = json.loads(f.read())
                        f.close()
                    processed_json = format(data)
                with open(file_name + "fixed", "w") as f:
                    f.write(json.dumps(processed_json, indent=4))
            except FileNotFoundError:
                # list the files in the current directory
                print("File not found. Please check the file name and try again.")
                print("Files in the current directory:")
                # print(os.listdir())
                continue

        elif choice == "3":
            file_name = input("Enter the name of the JSON file: ")
            date = input("Enter the date (YYYY-MM-DD): ")
            word = input("Enter the word to filter by: ")
            get_fresh(file_name, date, word)
            sort_json(filtered_file)
        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
