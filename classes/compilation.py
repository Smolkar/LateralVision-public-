import sys
import uuid
from classes.event import Event


class Compilation:
    """The `Compilation` class represents a compilation of events that are related to an RDP session. It contains information about the user, device, domain, start and end dates, source IP, description, session ID, impersonation, workstation source name, authentication package, cross domain status, FQDN, logon ID, logon type, and source domain.

    Attributes:
        unique_id (uuid.UUID): The unique ID of the compilation.
        user (str): The username associated with the compilation.
        device_name (str): The name of the device associated with the compilation.
        domain_name (str): The name of the domain associated with the compilation.
        start_date (datetime.datetime): The start date and time of the RDP session.
        end_date (datetime.datetime): The end date and time of the RDP session.
        source_ip (str): The source IP address of the RDP session.
        events (list): A list of `Event` objects that are associated with the RDP session.
        description (str): A description of the RDP session, based on the last event in the compilation.
        sessionid (int): The session ID associated with the RDP session.
        impersonation (bool): Whether impersonation was used during the RDP session.
        workstation_source_name (str): The name of the workstation that initiated the RDP session.
        authentication_package (str): The authentication package that was used during the RDP session.
        cross_domain (bool): Whether the RDP session crossed domains.
        fqdn (str): The fully qualified domain name of the device associated with the RDP session.
        logon_id (int): The logon ID associated with the RDP session.
        logon_type (list): A list of logon types associated with the RDP session.
        source_domain (str): The source domain associated with the RDP session.

    Methods:
        label_events(): Sets the description of the RDP session based on the last event in the compilation.
        set_cross_domain(): Sets the cross domain status of the RDP session based on the domain name and source domain.
        add_props(event): Adds properties to the RDP session based on the given event.
        add_event(event, exclude=None): Adds the given event to the RDP session if it is not excluded and updates the RDP session's properties accordingly. Returns an error code if there is an issue adding the event.
        to_string(): Returns a string representation of the RDP session."""

    def __init__(self, user):
        """
        This function is used to create a new object of the class Session

        :param user: The user that is logging on
        """

        self.unique_id = uuid.uuid4()
        self.user = None
        self.device_name = None
        self.domain_name = None
        self.start_date = None
        self.end_date = None
        self.source_ip = None
        self.events = []
        self.description = None
        self.sessionid = None
        self.impersonation = None
        self.workstation_source_name = None
        self.authentication_package = None
        self.cross_domain = False
        self.fqdn = None
        self.logon_id = None
        self.logon_type = []
        self.source_domain = None

    @property
    def description(self):
        """
        The function description() returns the value of the private variable _description
        :return: The description of the question.
        """
        return self._description

    @description.setter
    def description(self, value):
        """
        The function description() takes in two arguments, self and value. It then sets the value of the
        variable _description to the value of the argument value

        :param value: The value of the parameter
        """
        self._description = value

    def label_events(self):
        if self.events:
            last_event = self.events[-1]
            if last_event.eventid == 22:
                self.description = "Successful logon"
            if last_event.eventid == 4624:
                self.description = "Network logon"
            if last_event.eventid == 1149:
                self.description = "Open RDP application"
            if last_event.eventid == 4625:
                self.description = "Incorrect username or password"
            if last_event.eventid == 4647:
                self.description = "Initiated logoff"
            if last_event.eventid == 4634:
                self.description = "Logoff"
            if last_event.eventid == 9009:
                self.description = "Disconnected"
            if last_event.eventid == 4778:
                self.description = "Reconnected"
            if last_event.eventid == 25:
                self.description = "Reconnected"
            if last_event.eventid == 23:
                self.description = "Disconnected"

    def set_cross_domain(self):
        """
        If the domain name is not the same as the source domain, then the cross domain is true
        """
        if self.domain_name != self.source_domain and self.source_domain:
            self.cross_domain = True

    def add_props(self, event):
        """
        The function adds properties to the session object if the event is not in the list of event IDs

        :param event: The event object that is being processed
        """
        if event:
            self.domain_name = self.domain_name or event.domain
            self.device_name = self.device_name or event.device_name
            self.fqdn = self.fqdn or event.fqdn

            if event.eventid not in [40]:
                self.user = self.user or event.user
            if event.eventid not in [23, 4647, 40]:
                self.source_ip = self.source_ip or event.source_ip

            if event.eventid not in [21, 22, 24, 40]:
                self.source_domain = self.source_domain or event.source_domain
            if event.eventid in [21, 22, 23, 24, 25]:
                self.sessionid = self.sessionid or event.sessionid
            if event.eventid in [4624, 4625, 4634]:
                self.logon_type.append(event.logon_type)
            if event.eventid in [4625, 4524]:
                self.workstation_source_name = (
                    self.workstation_source_name or event.source_name
                )

                self.authentication_package = (
                    self.authentication_package or event.auth_package
                )
            if event.eventid in [4624]:
                self.impersonation = self.impersonation or event.impersonation
            if event.eventid in [4625, 4624, 4634, 4647]:
                self.logon_id = self.logon_id or event.logon_id

    def add_event(self, event, exclude=None):
        """
        The function takes in an event, and if the event is not excluded, it adds the event to the
        compilation.

        The function also checks if the event is an instance of the Event class, and if the event is
        not, it raises a ValueError.

        The function also checks if the event is in the exclude list, and if it is, it returns a string.


        The function also checks if the event's fqdn is the same as the compilation's fqdn, and if it is
        not, it returns 110.

        The function also checks if the event's domain is the same as the compilation's domain name, and
        if it is not, it returns 111.

        The function also checks if the event's device name is the same as the compilation's device
        name, and if it is not, it returns 112.

        The function also checks if the event's user is the same as the

        :param event: The event to be added to the compilation
        :param exclude: a list of IP addresses that should be excluded from the compilation
        :return: The return value is the result of the add_event function.
        """
        # Check if the event is an instance of the Event class
        if not isinstance(event, Event):
            raise ValueError("Event must be an instance of the Event class")
        # checks if the event is in the exclude list
        if event.source_ip in exclude:
            return "This event is excluded"
        # In any other case, add the event to the compilation
        else:
            if self.fqdn and event.fqdn != self.fqdn:
                return 110
            if self.domain_name and event.domain != self.domain_name:
                return 111
            if self.device_name and event.device_name != self.device_name:
                return 112
            if self.user and event.user != self.user:
                return 113

            # Add the event to the list of events for this compilation
            self.events.append(event)

            self.add_props(event)

            if (
                self.start_date
                and event.event_time < self.start_date
                and event.device_name == self.device_name
            ):
                return f"Weird the event is not in order YOU NEEED TO CHECK - \
                    {event.event_record_id}"

            if event.eventid in [4624, 4625, 4634] and self.logon_id == event.logon_id:
                self.end_date = event.event_time
                self.label_events()
                self.set_cross_domain()

                return 1

            if event.eventid in [4624, 4625, 4634] and self.logon_id != event.logon_id:
                return 100
            if event.eventid in [22, 9009, 4778]:
                if not self.end_date:
                    self.end_date = event.event_time
                    self.label_events()
                    self.set_cross_domain()

                    return 1
                else:
                    return 100
            if event.eventid in [1149, 24, 23]:
                self.start_date = event.event_time
                self.label_events()
                self.set_cross_domain()
                return 1
            if not self.start_date:
                self.start_date = event.event_time
                return 1

    def to_string(self):
        """
        This function takes the object's attributes and returns a string with the attributes in a
        readable format
        :return: A string of the object's attributes.
        """
        return f"""
        Unique ID: {self.unique_id}
        User: {self.user}
        Device Name: {self.device_name}
        Domain Name: {self.domain_name}
        Start Date: {self.start_date}
        End Date: {self.end_date}
        Source IP: {self.source_ip}
        Description: {self.description}
        Session ID: {self.sessionid}
        Impersonation: {self.impersonation}
        Workstation Source Name: {self.workstation_source_name}
        Authentication Package: {self.authentication_package}
        Cross Domain: {self.cross_domain}
        FQDN: {self.fqdn}
        Logon ID: {self.logon_id}
        Logon Type: {self.logon_type}
        Source Domain: {self.source_domain}
        """
