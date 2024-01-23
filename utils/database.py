from py2neo import Graph, Node, Relationship, ServiceUnavailable
import os
import sys
import time
from neo4j import GraphDatabase

# Import the module from the classes directory
# using an absolute import statement
from classes.user import User
from classes.device import Device
from classes.compilation import Compilation
from classes.domain import Domain
from classes.event import Event


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)
cwd = os.path.abspath(os.getcwd())
model_path = os.path.join(cwd, "resources", "model")
resources_path = os.path.join(cwd, "resources")
uploads_path = os.path.join(cwd, "resources", "uploads")
processed_path = os.path.join(cwd, "resources", "processed")
while True:
    try:
        graph = Graph("neo4j://neo4j:7687", auth=("neo4j", "password"))
        # graph = Graph("neo4j://localhost:7687", auth=("neo4j", "password"))

        graph.run("MATCH (n) RETURN n LIMIT 1")
        print("Neo4j is available")
        break
    except ServiceUnavailable:
        print("Neo4j is unavailable - sleeping")
        time.sleep(5)


def create_device_node(device):
    device_node = Node(
        "Device", unique_id=str(device._unique_id), name=device._name
    )  # E501
    graph.create(device_node)
    return device_node


def create_compilation_node(compilation):
    compilation_node = Node(
        "Compilation",
        unique_id=str(compilation.unique_id),
        user=compilation.user,
        device_name=compilation.device_name,
        domain_name=compilation.domain_name,
        start_date=compilation.start_date,
        end_date=compilation.end_date,
        source_ip=compilation.source_ip,
        description=compilation.description,
        sessionid=compilation.sessionid,
        impersonation=compilation.impersonation,
        workstation_source_name=compilation.workstation_source_name,
        authentication_package=compilation.authentication_package,
        cross_domain=compilation.cross_domain,
        fqdn=compilation.fqdn,
        logon_id=compilation.logon_id,
        logon_type=compilation.logon_type,
        source_domain=compilation.source_domain,
    )
    graph.create(compilation_node)
    return compilation_node


def create_relative_correlation_node():
    query = """
    MATCH (e:Event)
    WHERE e.source_name IS NOT NULL AND e.source_ip IS NOT NULL AND e.source_ip <> "::" AND e.source_name <> "-"
    MERGE (w:Workstations {source_name: e.source_name})
    MERGE (ip:Workstation_IP {source_ip: e.source_ip})
    MERGE (w)-[:HAS_IP]->(ip)
    """

    with GraphDatabase.driver(
        "bolt://neo4j:7687", auth=("neo4j", "password")
    ) as driver:
        with driver.session() as session:
            session.run(query)


def create_domain_node(domain):
    domain_node = Node(
        "Domain", unique_id=str(domain.unique_id), name=domain.name
    )  # E501
    graph.create(domain_node)
    return domain_node


def create_event_node(event):
    if len(event.source_name) > 0:
        event.source_name = event.source_name[0]

    event_node = Node(
        "Event",
        unique_id=str(event._unique_id),
        event_record_id=event.event_record_id,
        event_time=event.event_time,
        eventid=event.eventid,
        domain_name=event.domain,
        device_name=event.device_name,
        source_ip=event.source_ip,
        source_name=event.source_name,
        user=event.user,
        channel=event.channel,
        logon_type=event.logon_type,
        auth_package=event.auth_package,
        sessionid=event.sessionid,
        logon_id=event.logon_id,
        fqdn=event.fqdn,
        impersonation=event.impersonation,
        source_domain=event.source_domain,
    )
    graph.create(event_node)
    return event_node


def create_user_node(user):
    user_node = Node(
        "User",
        unique_id=str(user._unique_id),
        username=user._username,
        role=user._role,
        flag=user._flag,
    )
    graph.create(user_node)
    return user_node


def create_user_device_relationship(user_node, device_node):
    relationship = Relationship(user_node, "USES", device_node)
    graph.create(relationship)


def create_device_domain_relationship(device_node, domain_node):
    relationship = Relationship(device_node, "BELONGS_TO", domain_node)
    graph.create(relationship)


def create_user_compilation_relationship(user_node, compilation_node):
    relationship = Relationship(user_node, "GENERATES", compilation_node)
    graph.create(relationship)


def create_event_compilation_relationship(event_node, compilation_node):
    relationship = Relationship(event_node, "OCCURS_IN", compilation_node)
    graph.create(relationship)


def create_event_user_relationship(event_node, user_node):
    relationship = Relationship(event_node, "INVOLVES", user_node)
    graph.create(relationship)


# Add this function to validate names
def is_invalid_name(name):
    invalid_names = ["", " ", "-", "NULL", "null", "None", "none", "N/A", "n/a"]
    return name in invalid_names or name is None


def init_db(domains):
    for domain_name, domain in domains.items():
        if is_invalid_name(domain_name):
            print(f"Skipping domain with invalid name '{domain_name}'")
            continue

        domain_node = create_domain_node(domain)

        if not domain.devices:
            print(f"Skipping domain '{domain_name}' without devices")
            continue

        for device in domain.devices:
            if is_invalid_name(device._name):
                print(f"Skipping device with invalid name '{device._name}'")
                continue

            device_node = create_device_node(device)
            create_device_domain_relationship(device_node, domain_node)

            if not device._users:
                print(f"Skipping device '{device._name}' without users")
                continue

            for user in device._users:
                if is_invalid_name(user._username):
                    print(f"Skipping user with invalid name '{user._username}'")
                    continue

                user_node = create_user_node(user)
                create_user_device_relationship(user_node, device_node)

                if not user._compilations:
                    print(
                        f"Skipping user '{user._username}' without compilations"
                    )  # E501
                    continue

                for compilation in user._compilations:
                    if not compilation.events:
                        print(
                            f"Skipping compilation '{compilation.description}' without events"  # E501
                        )
                        continue

                    compilation_node = create_compilation_node(compilation)
                    create_user_compilation_relationship(
                        user_node, compilation_node
                    )  # E501

                    for event in compilation.events:
                        event_node = create_event_node(event)
                        create_event_compilation_relationship(
                            event_node, compilation_node
                        )
