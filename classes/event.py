import uuid


class Event:
    """
    A class representing an event in a Windows event log.

    Attributes:
    -----------
    event_record_id : int
        The unique identifier of the event.
    event_time : datetime.datetime
        The time when the event occurred.
    eventid : int
        The event ID.
    domain : str
        The name of the domain in which the event occurred.
    device_name : str
        The name of the device on which the event occurred.
    source_ip : str
        The IP address of the device that generated the event.
    source_name : str
        The name of the device that generated the event.
    user : str
        The name of the user associated with the event.
    channel : str
        The name of the event log channel.
    logon_type : int
        The type of logon associated with the event.
    auth_package : str
        The authentication package used for the logon.
    sessionid : int
        The session ID associated with the event.
    logon_id : int
        The logon ID associated with the event.
    fqdn : str
        The fully qualified domain name of the device that generated the event.
    impersonation : bool
        Whether the user was impersonated during the logon.
    source_domain : str
        The domain of the device that generated the event.

    Methods:
    --------
    to_string():
        Returns a string representation of the event.
    """

    def __init__(

        self,
        event_record_id,
        event_time,
        eventid,
        domain_name,
        device_name,
        source_ip,
        source_name=None,
        user=None,
        channel=None,
        logon_type=None,
        auth_package=None,
        session_id=None,
        logon_id=None,
        fqdn=None,
        impersonation=None,
        source_domain=None,
    ):
        """
        This function takes in a bunch of arguments and assigns them to the object's attributes

        :param event_record_id: The event record ID from the Windows event log
        :param event_time: The time the event was recorded on the device
        :param eventid: The event ID of the event
        :param domain_name: The domain name of the device that generated the event
        :param device_name: The name of the device that the event was recorded on
        :param source_ip: The IP address of the source machine
        :param source_name: The name of the computer that generated the event
        :param user: The user who logged on
        :param channel: The channel the event was logged to
        :param logon_type: 
        :param auth_package: The authentication package used to authenticate the user
        :param session_id: The session ID of the user who logged on
        :param logon_id: A unique identifier for the logon session
        :param fqdn: Fully Qualified Domain Name
        :param impersonation: The impersonation level of the logon
        :param source_domain: The domain of the source computer
        """
        self._unique_id = uuid.uuid4()  #
        self.event_record_id = event_record_id  #
        self.event_time = event_time  #
        self.eventid = eventid  #
        self.domain = domain_name  #
        self.device_name = device_name  #
        self.source_ip = source_ip  #
        self.source_name = source_name  #
        self.user = user  #
        self.channel = channel  #
        self.logon_type = logon_type  #
        self.auth_package = auth_package  #
        self.sessionid = session_id  #
        self.logon_id = logon_id
        self.fqdn = fqdn  #
        self.impersonation = impersonation  #
        self.source_domain = source_domain

    @property
    def id(self):
        """
        The function id() returns the unique id of the object
        :return: The unique id of the object.
        """
        return self._unique_id

    def to_string(self):
        """
        This function takes the object and returns a string with the object's attributes
        :return: The event record id, event id, event time, source ip, channel, logon type, auth
        package, user, domain, device name, source name, session id, logon id, fqdn, impersonation, and
        source domain.
        """
        return f"{self.event_record_id}----Event: {self.eventid} - {self.event_time} - {self.source_ip} - {self.channel} - {self.logon_type} - {self.auth_package} - {self.user} - {self.domain} - {self.device_name} - {self.source_name} - {self.sessionid} - {self.logon_id} - {self.fqdn} - {self.impersonation} - {self.source_domain}"
