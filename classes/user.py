from uuid import uuid4
import sys
from classes.compilation import Compilation


class User:
    """A class representing a user in the system.

    Attributes:
        _unique_id (uuid.UUID): The unique ID of the user.
        _username (str): The name of the user.
        devices (list): A list of devices associated with the user.
        _compilations (list): A list of compilations associated with the user.
        sessions (list): A list of sessions associated with the user.
        _role (str): The role of the user.
        _flag (bool): A flag indicating whether the user is flagged for further investigation.

    Methods:
        add_compilation(compilation: Compilation) -> None:
            Add a compilation to the list of compilations associated with this user.
        to_string() -> str:
            Returns a string representation of the user."""

    def __init__(self, username):
        """
        The function __init__() is a special function in Python classes. It is run as soon as an object
        of a class is instantiated. The method __init__() is analogous to constructors in C++ and Java.

        :param username: The username of the user
        """
        self._unique_id = uuid4()
        self._username = username
        self.devices = []
        self._compilations = []
        self.sessions = []  # add this property
        self._role = None  # add this property
        self._flag = None  # add this property

    @property
    def unique_id(self):
        """
        This function returns the unique ID of the user
        :return: The unique ID of the user.
        """
        """Get the unique ID of this user."""
        return self._unique_id

    @unique_id.setter
    def unique_id(self, value):
        """
        Set the unique ID of this user.

        :param value: The value to set the unique ID to
        """
        self._unique_id = value

    @property
    def username(self):
        """Get the name of this user."""
        return self._username

    @username.setter
    def username(self, value):
        """
        It takes a value, checks that it's a string, checks that it's alphanumeric, and then sets it as
        the value of the _name attribute

        :param value: The value that is being assigned to the attribute
        """
        if not isinstance(value, str):
            raise ValueError("Username must be a string")
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
        self._name = value

    @property
    def compilations(self):
        """
        It returns the value of the variable _compilations.
        :return: The list of compilations.
        """
        return self._compilations

    # @property
    # def sessions(self):
    #     """Get the list of sessions associated with this user."""
    #     return self._sessions

    @property
    def role(self):
        """Get the role of this user."""
        return self._role

    @role.setter
    def role(self, value):
        """Set the role of this user."""
        self._role = value

    @property
    def flag(self):
        """Get the flag of this user."""
        return self._flag

    @flag.setter
    def flag(self, value):
        """Set the flag of this user."""
        self._flag = value

    def add_compilation(self, compilation):
        """Add a compilation to the list of compilations associated with this user."""
        if isinstance(compilation, Compilation):
            self._compilations.append(compilation)
        else:
            raise ValueError("Compilation must be an instance of the Compilation class")

    def to_string(self):
        return f"{self.username}"
