import uuid


class Domain:
    """A class representing a Windows domain.

    Attributes:
        unique_id (uuid.UUID): A unique identifier for the domain.
        name (str): The name of the domain.
        users (list): A list of User objects associated with the domain.
        devices (list): A list of Device objects associated with the domain.

    """

    def __init__(self, name):
        """
        Initializes a new instance of the Domain class with the given name.

        :param name: The name of the domain.
        :type name: str
        """
        self.unique_id = uuid.uuid4()
        self.name = name
        self.users = []
        self.devices = []

    @property
    def name(self):
        """
        Gets or sets the name of the domain.

        :return: The name of the domain.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Sets the name of the domain.

        :param value: The name of the domain.
        :type value: str
        """
        self._name = value

    @property
    def unique_id(self):
        """
        Gets or sets the unique identifier of the domain.

        :return: The unique identifier of the domain.
        :rtype: UUID
        """
        return self._unique_id

    @unique_id.setter
    def unique_id(self, value):
        """
        Sets the unique identifier of the domain.

        :param value: The unique identifier of the domain.
        :type value: UUID
        """
        self._unique_id = value

    @property
    def users(self):
        """
        Gets or sets the list of users associated with the domain.

        :return: The list of users associated with the domain.
        :rtype: list
        """
        return self._users

    @users.setter
    def users(self, value):
        """
        Sets the list of users associated with the domain.

        :param value: The list of users associated with the domain.
        :type value: list
        """
        self._users = value

    @property
    def devices(self):
        """
        Gets or sets the list of devices associated with the domain.

        :return: The list of devices associated with the domain.
        :rtype: list
        """
        return self._devices

    @devices.setter
    def devices(self, value):
        """
        Sets the list of devices associated with the domain.

        :param value: The list of devices associated with the domain.
        :type value: list
        """
        self._devices = value
