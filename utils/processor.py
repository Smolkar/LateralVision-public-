from datetime import datetime, timezone
import datetime as dt
import string
import os
import sys
import random
import json
import pickle
import re

import changefinder
import joblib
from hmmlearn import hmm
import pandas as pd
import numpy as np
from classes.user import User
from classes.device import Device
from classes.compilation import Compilation
from classes.domain import Domain
from classes.event import Event
from utils import utils

# Add the parent directory of the script to the Python module search path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)
# cwd = os.path.abspath(os.getcwd())
# model_path = os.path.join(cwd, "resources", "model")
# resources_path = os.path.join(cwd, "resources")
# uploads_path = os.path.join(cwd, "resources", "uploads")
# processed_path = os.path.join(cwd, "resources", "processed")
CWD = os.path.abspath(os.getcwd())
MODEL_PATH = os.path.join(CWD, "resources", "model")
RESOURCES_PATH = os.path.join(CWD, "resources")
UPLOADS_PATH = os.path.join(RESOURCES_PATH, "uploads")
PROCESSED_PATH = os.path.join(RESOURCES_PATH, "processed")

# Import the module from the classes directory
# using an absolute import statement


np.random.seed(47)


def json_extract(obj, key):
    """
    It takes a JSON object and a key, and returns an array of all the values
    in the object that match
    the key

    :param obj: The JSON object to extract from
    :param key: The key to search for in the JSON object
    :return: A list of values from the JSON object.
    """
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    try:
        values = extract(obj, arr, key)
        return values
    except Exception as e:
        print("Error: {}".format(e))


exclude = ["LOCAL", None, "", "-", "127.0.0.1", "null"]


def process_events(json_data):
    """
    It takes a list of events, and returns a list of domains, each of which
    contains a list of devices,
    each of which contains a list of users, each of which contains a list of
    compilations, each of which
    contains a list of events

    :param json_data: The JSON data that you want to process
    :return: A dictionary of domains, each domain has a list of devices, each
    device has a list of
    users, each user has a list of compilations, each compilation has a list
    of events.
    """
    domains = {}
    pattern = r"^[^.]+"
    pattern_source = r"^[^.]+.([^.]+)"
    buffer_events = []
    user_name = None
    source_name = None
    logon_type = None
    auth_package = None
    session_id = None
    logon_id = None
    usr_obj = None
    # Loop through each event in the JSON data
    for event_data in json_data:
        event_record_id = event_data.get("EventRecordID")
        event_date = datetime.fromisoformat(
            event_data.get("EventTime").rstrip("Z")
        )  # E501
        event_id = event_data.get("EventID")

        # Extract relevant data from the event data
        domain_name = json_extract(event_data, "Account Domain")
        if len(domain_name) < 3:
            domain_name = event_data.get("DomainName").upper()
        try:
            domain_name = re.search(pattern, domain_name).group()
        except AttributeError:
            domain_name = event_data.get("DomainName").upper()

        device_name = event_data.get("Computer")
        try:
            device_name = re.search(pattern, device_name).group()
        except AttributeError:
            pass
        source_ip = event_data.get("SourceIP")

        # if event_id in [4625, 4624]:
        source_name = json_extract(event_data, "Workstation Name")
        # try:
        #     if len(source_name) > 0:
        #         source_name = re.search(pattern, source_name[0]).group()
        # except AttributeError:
        #     pass
        auth_package = json_extract(event_data, "Authentication Package")
        if len(auth_package) > 0:
            auth_package = auth_package[0]
        # if event_id not in [40]:
        user_name = event_data.get("UserName")
        # elif event_id in [4625, 4624, 4634]:
        logon_type = event_data.get("LogonType")
        logon_id = json_extract(event_data, "Logon ID")
        try:
            if len(logon_id) > 0:
                logon_id = logon_id[0]  # type: ignore
                if logon_id == "0":
                    logon_id = None
        except AttributeError:
            pass
        # elif event_id in [21, 22, 23, 24, 25]:
        session_id = json_extract(event_data, "Session ID")
        # elif event_id in [4647]:
        try:
            if session_id:
                session_id = session_id[0]
        except AttributeError:
            pass
        source_domain = event_data.get("Computer")
        source_domain = re.search(pattern_source, source_domain).group(
            1
        )  # type: ignore
        source_domain = source_domain.upper()
        channel = event_data.get("Channel")

        fqdn = json_extract(event_data, "Fqdn")[0]
        impersonation = json_extract(event_data, "Impersonation Level")
        if len(impersonation) > 0:
            impersonation = impersonation[0]
        #     continue
        event = Event(
            event_record_id,
            event_date,
            event_id,
            source_domain,
            device_name,
            source_ip,
            source_name,
            user_name,
            channel,
            logon_type,
            auth_package,
            session_id,
            logon_id,
            fqdn,
            impersonation,
            domain_name,
        )
        # Get or create the compilation associated with this event
        domain = domains.setdefault(domain_name, Domain(domain_name))
        device_obj = next(
            (d for d in domain.devices if d._name == device_name), None
        )  # E501
        if device_obj is None:
            device_obj = Device(device_name)
            domain.devices.append(device_obj)

        if event.eventid in [40]:
            buffer_events.append(event)

        else:
            # type: ignore
            usr_obj = next(
                (u for u in device_obj._users if u.username == user_name), None
            )
            if usr_obj is None:
                usr_obj = User(user_name)
                device_obj._users.append(usr_obj)  # type: ignore
            # compilation = Compilation(usr_obj)
            active_compilation = None
            if usr_obj.compilations:
                # check for incomplete compilation which maches the source n
                # ame domain and device name
                active_compilation = next(
                    (
                        c
                        for c in usr_obj.compilations
                        if c.source_ip == source_ip
                        and c.fqdn == fqdn
                        and c.end_date is None
                    ),
                    None,
                )
            if active_compilation is not None:
                if buffer_events:
                    for a in buffer_events:
                        active_compilation.add_event(a, exclude)
                    buffer_events.clear()

                result = active_compilation.add_event(event, exclude)
                if result != 1:
                    new_compilation = Compilation(usr_obj)
                    new_compilation.add_event(event, exclude)
                    usr_obj.add_compilation(new_compilation)
                else:
                    continue
            else:
                new_compilation = Compilation(usr_obj)
                if buffer_events:
                    for event in buffer_events:
                        new_compilation.add_event(event, exclude)
                    buffer_events.clear()

                result = new_compilation.add_event(event, exclude)
                if result != 1:
                    compilation1 = Compilation(usr_obj)
                    compilation1.add_event(event, exclude)
                    usr_obj.add_compilation(compilation1)
                else:
                    usr_obj.add_compilation(new_compilation)

    return domains


def get_domains(data):
    """
    It takes a dictionary of domains and returns a list of domains and a list
    of devices

    :param data: the data structure that contains all the information about
    the devices and domains
    :return: A list of domains and a list of devices
    """
    domains = []
    devices = []
    for domain in data:
        domains.append(domain)
        for device in data[domain].devices:
            devices.append(device._name)
    return domains, devices


def connections(data, start_date=None, end_date=None):
    """
    It takes in a dictionary of domains, and returns a dictionary of nodes
    and relationships

    :param data: The data that we want to visualize
    :return: A dictionary with two keys, nodes and relationships.
    """
    domains = data
    nodes = {}
    relationships = []
    relationship_id = 0

    def is_within_time_frame(compilation_start, compilation_end):
        if start_date is not None and compilation_start < start_date:
            return False
        if end_date is not None and compilation_end > end_date:
            return False
        return True

    def relationship_exists(start_id, end_id, rel_type, date_start, date_end):
        """
        If the relationship type, start node, end node, start date, and end
        date all match, then return
        True. Otherwise, return False

        :param start_id: the id of the start node
        :param end_id: The id of the node that the relationship is pointing to
        :param rel_type: The type of relationship we're looking for
        :param date_start: The start date of the relationship
        :param date_end: The end date of the relationship
        :return: A list of dictionaries.
        """
        for rel in relationships:
            if (
                rel["type"] == rel_type
                and (
                    (rel["startNode"] == start_id and rel["endNode"] == end_id)
                    or (
                        rel["startNode"] == end_id
                        and rel["endNode"] == start_id  # E501
                    )  # E501
                )
                and (
                    date_start is None
                    or rel["properties"].get("date_start") == date_start
                )
                and (
                    date_end is None
                    or rel["properties"].get("date_end") == date_end  # E501
                )  #
            ):
                return True
        return False

    def get_or_create_node(nodes, label, properties):
        for node in nodes.values():
            if node["labels"] == [label] and node["properties"] == properties:
                return node["id"]
        new_id = str(len(nodes))
        node = {
            "id": new_id,
            "labels": [label],
            "properties": properties,
        }
        nodes[new_id] = node
        return new_id

    for domain, domain_obj in domains.items():
        if (
            domain == "NULL"
            or not domain_obj.devices
            or domain == "LOCAL"
            or domain == "NT AUTHORITY"
            or domain == "-"
        ):
            continue

        for device in domain_obj.devices:
            if (
                device._name == "NULL"
                or device._name == ""
                or device._name == "-"
                or device._name == "vagrant"
                or device._name == "localhost"
                or device._name == "local"
                or device._name == "null"
            ):
                continue

            for user in device._users:
                if (
                    user.username == "NULL"
                    or user.username == ""
                    or user.username == "-"
                    or user.username == "vagrant"
                    or user.username == "localhost"
                    or user.username == "local"
                    or user.username == "null"
                ):
                    continue

                for compilation in user.compilations:
                    if (
                        compilation.description == "Successful logon"
                        and is_within_time_frame(
                            compilation.start_date, compilation.end_date
                        )
                    ):
                        domain_node_id = get_or_create_node(
                            nodes, "Domain", {"name": domain, "domain": domain}
                        )

                        device_node_id = get_or_create_node(
                            nodes,
                            "Device",
                            {"name": device._name, "domain": domain},  # E501
                        )

                        domain_device_relationship = {
                            "id": str(relationship_id),
                            "type": "Contains_Device",
                            "startNode": domain_node_id,
                            "endNode": device_node_id,
                            "properties": {},
                        }
                        if not relationship_exists(
                            domain_device_relationship["startNode"],
                            domain_device_relationship["endNode"],
                            domain_device_relationship["type"],
                            None,
                            None,
                        ):
                            relationships.append(domain_device_relationship)
                            relationship_id += 1

                        source_name = aquire_workstation_name(
                            domains, compilation.source_ip
                        )

                        if (
                            source_name is None
                            or source_name == ""
                            or source_name == "NULL"
                            or source_name == "-"
                            or source_name == "vagrant"
                            or source_name == "localhost"
                            or source_name == "local"
                            or source_name == "null"
                        ):
                            source_name = compilation.source_ip
                        source_node_id = get_or_create_node(
                            nodes,
                            "Device",
                            {"name": source_name, "domain": domain},  # E501
                        )

                        relationship = {
                            "id": str(relationship_id),
                            "type": "RDP_Connection",
                            "startNode": source_node_id,
                            "endNode": device_node_id,
                            "properties": {
                                "date_start": compilation.start_date,
                                "date_end": compilation.end_date,
                            },
                        }

                        if not relationship_exists(
                            relationship["startNode"],
                            relationship["endNode"],
                            relationship["type"],
                            relationship["properties"]["date_start"],
                            relationship["properties"]["date_end"],
                        ):
                            relationships.append(relationship)
                            relationship_id += 1
                        user_node_id = get_or_create_node(
                            nodes,
                            "User",
                            {"name": user.username, "domain": domain},  # E501
                        )

                        relationship = {
                            "id": str(relationship_id),
                            "type": "Logs_In",
                            "startNode": user_node_id,
                            "endNode": source_node_id,
                            "properties": {
                                "date_start": compilation.start_date,
                                "date_end": compilation.end_date,
                            },
                        }
                        if not relationship_exists(
                            relationship["startNode"],
                            relationship["endNode"],
                            relationship["type"],
                            relationship["properties"]["date_start"],
                            relationship["properties"]["date_end"],
                        ):
                            relationships.append(relationship)
                            relationship_id += 1
    sorted_nodes = sorted(nodes.values(), key=lambda x: int(x["id"]))
    sorted_rels = sorted(relationships, key=lambda x: int(x["id"]))
    data = {"nodes": sorted_nodes, "relationships": sorted_rels}
    return data


def nice_connections(data, start_date=None, end_date=None):
    """
    It takes in a dictionary of domains, and returns a dictionary of nodes
    and relationships

    :param data: The data that we want to visualize
    :return: A dictionary with two keys, nodes and relationships.
    """
    domains = data
    nodes = {}
    relationships = []
    relationship_id = 0

    def is_within_time_frame(compilation_start, compilation_end):
        if start_date is not None and compilation_start < start_date:
            return False
        if end_date is not None and compilation_end > end_date:
            return False
        return True

    def relationship_exists(start_id, end_id, rel_type, date_start, date_end):
        """
        If the relationship type, start node, end node, start date, and end
        date all match, then return
        True. Otherwise, return False

        :param start_id: the id of the start node
        :param end_id: The id of the node that the relationship is pointing to
        :param rel_type: The type of relationship we're looking for
        :param date_start: The start date of the relationship
        :param date_end: The end date of the relationship
        :return: A list of dictionaries.
        """
        for rel in relationships:
            if (
                rel["type"] == rel_type
                and (
                    (rel["startNode"] == start_id and rel["endNode"] == end_id)
                    or (
                        rel["startNode"] == end_id
                        and rel["endNode"] == start_id  # E501
                    )  # E501
                )
                and (
                    date_start is None
                    or rel["properties"].get("date_start") == date_start
                )
                and (
                    date_end is None
                    or rel["properties"].get("date_end") == date_end  # E501
                )  #
            ):
                return True
        return False

    def get_or_create_node(nodes, label, properties):
        for node in nodes.values():
            if node["labels"] == [label] and node["properties"] == properties:
                return node["id"]
        new_id = str(len(nodes))
        node = {
            "id": new_id,
            "labels": [label],
            "properties": properties,
        }
        nodes[new_id] = node
        return new_id

    for domain, domain_obj in domains.items():
        if (
            domain == "NULL"
            or not domain_obj.devices
            or domain == "LOCAL"
            or domain == "NT AUTHORITY"
            or domain == "-"
        ):
            continue

        for device in domain_obj.devices:
            if (
                device._name == "NULL"
                or device._name == ""
                or device._name == "-"
                or device._name == "vagrant"
                or device._name == "localhost"
                or device._name == "local"
                or device._name == "null"
            ):
                continue

            for user in device._users:
                if (
                    user.username == "NULL"
                    or user.username == ""
                    or user.username == "-"
                    or user.username == "vagrant"
                    or user.username == "localhost"
                    or user.username == "local"
                    or user.username == "null"
                ):
                    continue

                for compilation in user.compilations:
                    if (
                        compilation.description == "Successful logon"
                        and is_within_time_frame(
                            compilation.start_date, compilation.end_date
                        )
                    ):
                        domain_node_id = get_or_create_node(
                            nodes, "Domain", {"name": domain, "domain": domain}
                        )

                        device_node_id = get_or_create_node(
                            nodes,
                            "Device",
                            {
                                "name": f"{device._name}_{compilation.start_date}",
                                "domain": domain,
                            },
                        )

                        domain_device_relationship = {
                            "id": str(relationship_id),
                            "type": "Contains_Device",
                            "startNode": domain_node_id,
                            "endNode": device_node_id,
                            "properties": {},
                        }
                        if not relationship_exists(
                            domain_device_relationship["startNode"],
                            domain_device_relationship["endNode"],
                            domain_device_relationship["type"],
                            None,
                            None,
                        ):
                            relationships.append(domain_device_relationship)
                            relationship_id += 1

                        source_name = aquire_workstation_name(
                            domains, compilation.source_ip
                        )

                        if (
                            source_name is None
                            or source_name == ""
                            or source_name == "NULL"
                            or source_name == "-"
                            or source_name == "vagrant"
                            or source_name == "localhost"
                            or source_name == "local"
                            or source_name == "null"
                        ):
                            source_name = compilation.source_ip
                        source_node_id = get_or_create_node(
                            nodes,
                            "Device",
                            {
                                "name": f"{source_name}_{compilation.start_date}",
                                "domain": domain,
                            },
                        )

                        relationship = {
                            "id": str(relationship_id),
                            "type": "RDP_Connection",
                            "startNode": source_node_id,
                            "endNode": device_node_id,
                            "properties": {
                                "date_start": compilation.start_date,
                                "date_end": compilation.end_date,
                            },
                        }

                        if not relationship_exists(
                            relationship["startNode"],
                            relationship["endNode"],
                            relationship["type"],
                            relationship["properties"]["date_start"],
                            relationship["properties"]["date_end"],
                        ):
                            relationships.append(relationship)
                            relationship_id += 1
                        user_node_id = get_or_create_node(
                            nodes,
                            "User",
                            {
                                "name": f"{user.username}_{compilation.start_date}",
                                "domain": domain,
                            },
                        )
                        relationship = {
                            "id": str(relationship_id),
                            "type": "Logs_In",
                            "startNode": user_node_id,
                            "endNode": source_node_id,
                            "properties": {
                                "date_start": compilation.start_date,
                                "date_end": compilation.end_date,
                            },
                        }
                        if not relationship_exists(
                            relationship["startNode"],
                            relationship["endNode"],
                            relationship["type"],
                            relationship["properties"]["date_start"],
                            relationship["properties"]["date_end"],
                        ):
                            relationships.append(relationship)
                            relationship_id += 1
    sorted_nodes = sorted(nodes.values(), key=lambda x: int(x["id"]))
    sorted_rels = sorted(relationships, key=lambda x: int(x["id"]))
    data = {"nodes": sorted_nodes, "relationships": sorted_rels}
    return data


def aquire_workstation_name(domains, ip):
    """
    It takes a dictionary of domains and an IP address as input, and returns the name of the workstation
    that the IP address is associated with

    :param domains: a dictionary of domains, where the key is the domain name and the value is the
    domain object
    :param ip: The IP address of the workstation you want to find the name of
    """
    pc = []
    for domain in domains:
        for device in domains[domain].devices:
            for user in device._users:
                for compilation in user.compilations:
                    if compilation.source_ip == ip:
                        print(str(compilation.workstation_source_name))
                    if compilation.workstation_source_name:
                        print(compilation.workstation_source_name)
                        return compilation.workstation_source_name


def process_file(file_name):
    file_ext = os.path.splitext(file_name)[1]

    if file_ext == ".json":
        with open(os.path.join(UPLOADS_PATH, file_name), "r") as f:
            try:
                print("Processing file: " + file_name)
                processed_json_one = utils.create_valid_json(
                    os.path.join(UPLOADS_PATH, file_name)
                )
                json_data = utils.format(processed_json_one)
            except json.decoder.JSONDecodeError:
                json_data = json.load(f)
    elif file_ext == ".csv":
        try:
            json_data = utils.convert_csv_to_json(os.path.join(UPLOADS_PATH, file_name))
            processed_json_one = utils.create_valid_json(
                os.path.join(UPLOADS_PATH, file_name)
            )
            try:
                json_data = utils.format(processed_json_one)
            except json.decoder.JSONDecodeError:
                json_data = json.load(f)
        except Exception as e:
            print(e)
            raise ValueError("Invalid file type")
    else:
        raise ValueError("Invalid file type")

    return json_data


def save_processed_data(file_name, domains):
    with open(
        os.path.join(
            PROCESSED_PATH,
            "processed_" + os.path.splitext(file_name)[0] + ".data",
        ),
        "wb",
    ) as p:
        pickle.dump(domains, p)


def get_all(file_name):
    """
    It takes a file name as input, checks the file extension, and
    if it's a json file, it processes the
    json file and saves the result to the processed directory. If it's a
    csv file, it converts the csv
    file to json, processes the json file, and saves the result to the
    processed directory.

    :param file_name: The name of the file to be processed
    """
    json_data = process_file(file_name)
    domains = process_events(json_data)
    save_processed_data(file_name, domains)


# with open("rdp.jsonfixed", "r") as f:
#     json_data = json.load(f)
def increment_event_count(count_array, event_id, row, column):
    """
    It takes a 3D array, an event ID, and a row and column, and increments the appropriate element in
    the array

    :param count_array: The array that will hold the counts of each event
    :param event_id: The event ID of the event
    :param row: The row of the matrix that the event will be placed in
    :param column: The column number of the event
    """
    event_map = {
        4624: 0,
        4625: 1,
        4647: 2,
        1149: 3,
        22: 4,
        9009: 5,
        4778: 6,
        25: 7,
        23: 8,
        4634: 9,
        21: 10,
    }
    if event_id in event_map:
        count_array[event_map[event_id], row, column] += 1


def randomString(stringLength=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return (
        "".join(random.choice(letters) for i in range(stringLength)) + ".model"
    )  # E501


def anomaly_detection(data, users, starttime, tohours):
    """
    It takes in the data, the list of users, the start time, and the
    number of hours to look at, and
    returns the count of each event for each user, the changefinder score for
    each user, the
    changefinder score for each user, and the count of each event for each user

    :param data: the dataframe containing the data
    :param users: list of users
    :param starttime: The start time of the data
    :param tohours: The number of hours to look at
    :return: the following:
    1. count_all_array: A list of lists containing the number of events for
    each user and event type.
    2. result_array: A list of lists containing the changefinder scores for
    each user and event type.
    3. cfdetect: A dictionary containing the maximum changefinder score for
    each user.
    4. count_array:
    """

    count_array = np.zeros((11, len(users), tohours + 1))
    count_all_array = []
    result_array = []
    cfdetect = {}

    for _, event in data.iterrows():
        if event["dates"] == "dates":
            pass

        column = int(
            (
                datetime.fromisoformat(event["dates"].replace("Z", "+00:00"))
                - starttime.replace(tzinfo=timezone.utc)
            ).total_seconds()
            / 3600
        )
        row = users.index(event["username"])
        event_id = event["eventid"]

        increment_event_count(count_array, event_id, row, column)

    count_sum = np.sum(count_array, axis=0)
    count_average = count_sum.mean(axis=0)
    num = 0
    for udata in count_sum:
        cf = changefinder.ChangeFinder(r=0.04, order=1, smooth=5)
        ret = []
        for i in count_average:
            cf.update(i)

        for i in udata:
            score = cf.update(i)
            ret.append(round(score, 2))
        result_array.append(ret)

        cfdetect[users[num]] = max(ret)

        count_all_array.append(udata.tolist())
        for var in range(0, 10):
            con = []
            for i in range(0, tohours):
                con.append(count_array[var, num, i])
            count_all_array.append(con)
        num += 1

    return count_all_array, result_array, cfdetect, count_array


# Calculate PageRank


def compute_pagerank(event_set, hmm, cf, admins=None, ntml=None):
    """
    It takes a graph of nodes and edges, and computes the PageRank of each node

    :param event_set: The dataframe containing the events
    :param hmm: a list of users that are known to be hackers
    :param cf: The confidence factor of the user
    :param admins: a list of admin accounts
    :param ntml: list of users that are not malicious
    :return: A dictionary of nodes and their pagerank scores.
    """
    graph = {}
    nodes = []
    for _, event in event_set.iterrows():
        nodes.append(event["ipaddress"])
        nodes.append(event["username"])

    for node in list(set(nodes)):
        links = []
        for _, event in event_set.iterrows():
            if node == event["ipaddress"]:
                links.append(event["username"])
            if node == event["username"]:
                links.append(event["ipaddress"])
        graph[node] = links

    numloops = 30
    ranks = {}
    d = {}
    npages = len(graph)
    for page in graph:
        if page and "@" in page[-1]:
            df = 0.85
        else:
            df = 0.8
        if hmm is not None and page in hmm:
            df -= 0.2
        if ntml is not None and page in ntml:
            df -= 0.1
        if admins is not None and page in admins:
            df = 0.6
        if page in cf:
            df -= cf[page] / 200
        d[page] = df
        ranks[page] = 1.0 / npages

    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d[page]) / npages
            for node in graph:
                if page in graph[node]:
                    newrank = newrank + d[node] * ranks[node] / len(
                        graph[node]
                    )  # E501  # E501
            newranks[page] = newrank
        ranks = newranks

    nranks = {}
    max_v = max(ranks.values())
    min_v = min(ranks.values())
    for key, value in ranks.items():
        nranks[key] = (value - min_v) / (max_v - min_v)

    return nranks


def is_valid_ip(ip):
    """
    It checks if the IP is valid by checking if it matches the regular
    expression

    :param ip: The IP address to check
    :return: The function is_valid_ip() is returning a boolean value.
    """
    # Regular expression for IPv4 and IPv6 validation
    ip_regex = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$|^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"

    # Check if the IP matches the regex
    if ip == "::1":
        return False
    if re.match(ip_regex, ip) == None:  # noqa: E711
        return False
    else:
        return True


def is_valid_username(username):
    """
    "If the username is not blank and is not in the list of invalid usernames,
    then it's valid."

    The above function is a good example of a function that is easy to read
    and understand

    :param username: The username to validate
    :return: True or False
    """
    if not username:
        return False
    if username in [""]:
        return False
    return True


def main_detection(data, admins=None, ntmlauth=None, model_name=randomString()):  # E501
    """
    It takes in a list of events, and returns a list of ranks, a list of
    detects, a list of timelines, a
    list of usernames, and a list of eventids

    :param data: The data that you want to analyze
    :param admins: A list of usernames that are admins
    :param ntmlauth: A list of NTLM authentication events
    """
    event_dicts = []
    count_dicts = []

    for event in data:
        username = event.get("UserName")
        if not is_valid_username(username):
            continue
        ip = event.get("SourceIP")
        if not is_valid_ip(ip):
            continue

        event_dict = {
            "id": event.get("EventRecordID"),
            "eventid": event.get("EventID"),
            "ipaddress": ip,
            "username": username,
            "logintype": event.get("LogonType"),
            "status": event.get("Description"),
            "authname": event.get("DomainName"),
            "date": datetime.fromisoformat(
                event["EventTime"].replace("Z", "+00:00")
            ).timestamp(),
        }
        event_dicts.append(event_dict)

        count_dict = {
            "dates": event["EventTime"],
            "eventid": event.get("EventID"),
            "username": username,
        }
        count_dicts.append(count_dict)

    event_set = pd.DataFrame(event_dicts)
    count_set = pd.DataFrame(count_dicts)

    username_set = event_set["username"].unique().tolist()

    ml_frame = event_set[["date", "username", "ipaddress", "eventid"]]
    ml_frame = ml_frame.copy()
    ml_frame["date"] = pd.to_datetime(ml_frame["date"], unit="s")
    ml_frame["date"] = ml_frame["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    starttime = min(event_set["date"])
    endtime = max(event_set["date"])
    starttime_a = datetime.fromtimestamp(int(starttime))
    endtime_a = datetime.fromtimestamp(int(endtime))
    tohours = int((endtime_a - starttime_a).total_seconds() / 3600)
    learnhmm(
        ml_frame, username_set, datetime.fromtimestamp(starttime), model_name
    )  # E501

    # Calculate ChangeFinder
    timelines, detects, detect_cf, eventids = anomaly_detection(
        count_set, username_set, datetime.fromtimestamp(starttime), tohours
    )

    # Calculate Hidden Markov Model
    detect_hmm = decode_hmm(
        ml_frame, username_set, datetime.fromtimestamp(starttime), model_name
    )
    ranks = compute_pagerank(event_set, admins, detect_hmm, detect_cf, ntmlauth)

    return ranks, detects, timelines, username_set, eventids


# random string generator


def decode_hmm(frame, users, start_time, model_name):
    """
    It takes in a dataframe, a list of users, and a start time, and
    returns a list of users that are
    detected as malicious

    :param frame: The dataframe containing the data
    :param users: A list of users to be checked for anomalies
    :param start_time: The start time of the data you want to analyze
    :return: a list of users that have been detected as malicious.
    """
    detected_users = []
    if not os.path.exists(model_path):
        os.makedirs(os.path.join(resources_path, "model"), exist_ok=True)

    model = joblib.load(os.path.join(model_path, model_name))
    while True:
        date = start_time.strftime("%Y-%m-%d")
        for user in users:
            hosts = np.unique(
                frame[(frame["username"] == user)].ipaddress.values
            )  # E501
            for host in hosts:
                udata = []
                for _, data in frame[
                    (frame["date"].str.contains(date))
                    & (frame["username"] == user)
                    & (frame["ipaddress"] == host)
                ].iterrows():
                    id = data["eventid"]
                    if id == 4624:
                        udata.append(0)
                    elif id == 4625:
                        udata.append(1)
                    elif id == 4647:
                        udata.append(2)
                    elif id == 4647:
                        udata.append(3)
                    elif id == 1149:
                        udata.append(4)
                    elif id == 22:
                        udata.append(5)
                    elif id == 9009:
                        udata.append(6)
                    elif id == 4778:
                        udata.append(7)
                    elif id == 25:
                        udata.append(8)
                    elif id == 23:
                        udata.append(9)
                    elif id == 21:
                        udata.append(10)
                if len(udata) > 2:
                    filtered_udata = [x for x in udata if 0 <= x <= 10]
                    if len(filtered_udata) > 2:
                        data_decode = model.predict(
                            np.array([np.array(filtered_udata)], dtype="int").T
                        )
                        unique_data = np.unique(data_decode)
                        if unique_data.shape[0] == 2:
                            if user not in detected_users:
                                detected_users.append(user)

        start_time += dt.timedelta(days=1)
        if frame.loc[(frame["date"].str.contains(date))].empty:
            break

    return detected_users


def learnhmm(frame, users, stime, model_name):
    """
    It takes a dataframe, a list of users, and a start date,
    and then it creates a HMM model that can be
    used to predict the next eventid given a sequence of eventids

    :param frame: The dataframe containing the data
    :param users: list of users to learn from
    :param stime: The start time of the data you want to learn from
    """
    lengths = []
    data_array = np.array([])
    model = hmm.CategoricalHMM(n_components=3, n_features=11, n_iter=10000)

    while True:
        date = stime.strftime("%Y-%m-%d")
        for user in users:
            hosts = np.unique(
                frame[(frame["username"] == user)].ipaddress.values
            )  # E501
            for host in hosts:
                udata = np.array([])
                for _, data in frame[
                    (frame["date"].str.contains(date))
                    & (frame["username"] == user)
                    & (frame["ipaddress"] == host)
                ].iterrows():
                    id = data["eventid"]
                    udata = np.append(udata, id)

                if udata.shape[0] > 2:
                    data_array = np.append(data_array, udata)
                    lengths.append(udata.shape[0])

        stime += dt.timedelta(days=1)
        if frame.loc[(frame["date"].str.contains(date))].empty:
            break

    data_array[data_array == 4624] = 0
    data_array[data_array == 4625] = 1
    data_array[data_array == 4647] = 2
    data_array[data_array == 1149] = 3
    data_array[data_array == 22] = 4
    data_array[data_array == 9009] = 5
    data_array[data_array == 4778] = 6
    data_array[data_array == 25] = 7
    data_array[data_array == 23] = 8
    data_array[data_array == 4634] = 9
    data_array[data_array == 21] = 10

    model.fit(np.array([data_array], dtype="int").T, lengths)
    joblib.dump(model, os.path.join(model_path, model_name))


def run():
    """
    It takes in the data, performs anomaly detection,
    and generates an HTML report
    """

    with open("rdp.jsonfixed") as f:
        data = json.load(f)

        # Perform anomaly detection and get results
    admins = []
    ntmlauth = []
    ranks, detects, timelines, username_set, count_array = main_detection(
        data, admins, ntmlauth, "Hello.model"
    )
    # domains = process_events(data)
    # Create dataframe to store results
    df = pd.DataFrame({"Username": username_set})

    # Add columns for event counts
    for period in ["Hour", "Day", "Week", "Month", "Year"]:
        for i in range(24 if period == "Hour" else 1, 0, -1):
            df[f"{period} {i}"] = np.nan

    # Fill in event counts for each user
    for i, username in enumerate(username_set):
        for period in ["Hour", "Day", "Week", "Month", "Year"]:
            period_length = (
                1
                if period == "Hour"
                else 30
                if period == "Month"
                else 7
                if period == "Week"
                else 365
                if period == "Year"
                else 1
            )
        for j in range(24 if period == "Hour" else 1, 0, -1):
            col_name = f"{period} {j}"
            time_period = (
                datetime.now() - pd.Timedelta(hours=j - 1)
                if period == "Hour"
                else datetime.now() - pd.Timedelta(days=j - 1)
                if period == "Day"
                else datetime.now() - pd.Timedelta(weeks=j - 1)
                if period == "Week"
                else datetime.now() - pd.Timedelta(days=j - 1)
                if period == "Month"
                else datetime.now() - pd.Timedelta(days=j - 1)
            )
            col_value = count_array[
                :, i, -j * period_length : -((j - 1) * period_length)  # E203
            ].sum()
            df.loc[i, col_name] = col_value

    # Sort by anomaly score and display the DataFrame
    df["Anomaly Score"] = [ranks.get(u, 0) for u in username_set]
    df = df.sort_values("Anomaly Score", ascending=False)
    # df = df[["Username", "Anomaly Score"] + list(df.columns[2:])]
    df = df.reset_index(drop=True)

    # Generate HTML report
    html = "<html>\n<head>\n<title>Anomaly Detector Results</title>\n</head>\n<body>\n"

    # Add table of user event counts
    html += "<h2>User Event Counts</h2>\n"
    html += df.to_html(index=False)

    # Add table of anomaly scores
    html += "<h2>User Anomaly Scores</h2>\n"
    html += df[["Username", "Anomaly Score"]].to_html(index=False)

    html += "\n</body>\n</html>"

    # Write HTML report to file
    with open("anomaly_detector_results.html", "w") as f:
        f.write(html)


# run()
