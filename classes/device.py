import uuid


class Device:
    """The Device class represents a device in the network. It has methods for adding a compilation to the list of compilations associated with the device.

    Class attributes

    _unique_id: A UUID unique identifier for the device.
    _name: A string representing the name of the device.
    _users: A list containing the names of the users associated with the device.
    _ips: A list containing the IP addresses associated with the device.
    _compilations: A list containing the compilations associated with the device.
    _sessions: A list containing the session IDs associated with the device.
    Methods

    add_compilation(compilation): Adds a compilation to the list of compilations associated with the device. The method raises a ValueError if the provided compilation is not an instance of the Compilation class.
    """

    def __init__(self, name):
        """
        This function creates a new instance of the class, and initializes the instance's attributes

        :param name: The name of the project
        """
        self._unique_id = uuid.uuid4()
        self._name = name
        self._users = []
        self._ips = []
        self._compilations = []
        self._sessions = []

    def add_compilation(self, compilation):
        """
        If the compilation is an instance of the Compilation class, add it to the list of compilations
        associated with this user

        :param compilation: The compilation to add to the list of compilations associated with this user
        """
        """Add a compilation to the list of compilations associated with this user."""
        if isinstance(compilation, Compilation):
            self._compilations.append(compilation)
        else:
            raise ValueError("Compilation must be an instance of the Compilation class")
