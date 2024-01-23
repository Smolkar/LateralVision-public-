import uuid


class Session:
    """
    A class that represents a session, which is a collection of compilations associated with a user.

    Attributes:
    -----------
    unique_id: uuid.UUID
        A unique identifier for the session.
    fqdn_source: str
        The fully qualified domain name of the source device.
    fqdn_destination: str
        The fully qualified domain name of the destination device.
    workstation_ip_source: str
        The IP address of the source device.
    workstation_name_source: str
        The name of the source device.
    workstation_ip_destination: str
        The IP address of the destination device.
    workstation_name_destination: str
        The name of the destination device.
    started_date: datetime.datetime
        The date and time when the session started.
    ended_date: datetime.datetime
        The date and time when the session ended.
    impersonation: str
        The type of impersonation used during the session, if any.
    domains: list
        A list of Domain objects associated with the session.
    compilations: list
        A list of Compilation objects associated with the session.
    session_id: int
        The ID of the session.
    flagged: bool
        A flag indicating whether the session has been flagged as potentially malicious.
    cross_domain: bool
        A flag indicating whether the session involves more than one domain.
    """

    def __init__(self, user):
        """
        The function takes a user as an argument and creates a new object with the following attributes:
        unique_id, fqdn_source, fqdn_destination, workstation_ip_source, workstation_name_source,
        workstation_ip_destination, workstation_name_destination, started_date, ended_date,
        impersonation, domains, compilations, session_id, flagged, and cross_domain

        :param user: The user that is being tracked
        """
        self.unique_id = uuid.uuid4()
        self.fqdn_source = None
        self.fqdn_destination = None
        self.workstation_ip_source = None
        self.workstation_name_source = None
        self.workstation_ip_destination = None
        self.workstation_name_destination = None
        self.started_date = None
        self.ended_date = None
        self.impersonation = None
        self.domains = []
        self.compilations = []
        self.session_id = None
        self.flagged = False
        self.cross_domain = False

    # SET property cross domain to true if the session has more than one domain
    def set_cross_domain(self):
        """
        If the number of domains is greater than 1, then the cross_domain is true. Otherwise, it's false
        """
        if len(self.domains) > 1:
            self.cross_domain = True
        else:
            self.cross_domain = False

    def set_props(self, compilation):
        """
        The function takes in a compilation object and sets the properties of the current object to the
        compilation object's properties

        :param compilation: the object that contains the data that I want to set the properties to
        """
        self.fqdn_source = compilation.fqdn
        self.workstation_ip_source = compilation.source_ip
        self.workstation_name_source = compilation.workstation_source_name
        self.session_id = compilation.sessionid
        self.impersonation = compilation.impersonation
        self.started_date = compilation.start_date
        self.ended_date = compilation.end_date

    def add_compilation(self, compilation):
        """
        It adds a compilation to the list of compilations.

        :param compilation: The compilation to add to the list of compilations
        """
        self.compilations.append(compilation)
