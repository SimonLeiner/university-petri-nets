"""
This module contains the Interface Patterns.

Interface Patterns can be synchronous and asynchronous or both.

Interface patterns are distinguished by the number of inter- acting parties:
    - Bilateral patterns specifying interactions between a pair of agents (IP-8);
    - Multilateral patterns specifying interactions among three or more agents.

Interface patterns are also classified according to the way agents interact:
    - Single transmission patterns (IP-1, IP-2, IP-3);
    - Multiple transmission patterns (IP-7).
"""

from abc import ABCMeta
from abc import abstractmethod

from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils import petri_utils


class BaseInterfacePattern(metaclass=ABCMeta):
    """
    Abstract base class for interface patterns.

    Comments:
        - This class defines the structure for all derived interface patterns (IP-1, IP-2, etc.).
        - An interface pattern is a generalized petri-net (GWF-Net) allowing sets of initial and final places rather than somgletons.
    """

    def __repr__(self) -> str:
        """String representation of the InterfacePattern object."""
        return f"<{self.__class__.__name__}>"

    def __init__(self, name: str) -> None:
        """
        Initializes the Petri net and markings.

        Args:
            name (str): The name of the Petri net.
        """
        # Initialize the Petri net
        self.net = PetriNet(name)

        # Initialize the initial and final markings
        self.initial_marking = Marking()
        self.final_marking = Marking()

    @abstractmethod
    def _define_places(self) -> None:
        """Define the places."""

    @abstractmethod
    def _define_transitions(self) -> None:
        """Define the transitions."""

    @abstractmethod
    def _define_arcs(self) -> None:
        """Define the arcs connecting places and transitions."""

    @abstractmethod
    def _define_markings(self) -> None:
        """Define the initial and final markings."""

    def get_net(self) -> tuple:
        """
        Returns the Petri net along with its initial and final markings.

        Returns:
            tuple: (net, initial_marking, final_marking)
        """
        return self.net, self.initial_marking, self.final_marking


class IP1(BaseInterfacePattern):
    """Defines the IP-1 interface pattern, involving Agent A1 sending a message and Agent A2 receiving it."""

    def __init__(self) -> None:
        """Initializes the IP-1."""
        # Call the superclass constructor
        super().__init__("IP-1")

        # define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p_A1 (Agent A1) and p_A2 (Agent A2).
        'Two Agents A1 and A2'.
        """
        # start places
        self.p_a1_start = PetriNet.Place("p_A1_start")
        self.p_a2_start = PetriNet.Place("p_A2_start")

        # new place
        self.p_a = PetriNet.Place("p_A")

        # end places
        self.p_a1_end = PetriNet.Place("p_A1_end")
        self.p_a2_end = PetriNet.Place("p_A2_end")

        self.net.places.add(self.p_a1_start)
        self.net.places.add(self.p_a2_start)
        self.net.places.add(self.p_a)
        self.net.places.add(self.p_a1_end)
        self.net.places.add(self.p_a2_end)

    def _define_transitions(self) -> None:
        """Defines transitions t_send (sending message) and t_receive (receiving message).
        'Single labeled transition used to send/recieve messages'.
        'Channels are added only in a single direction to send/recieve messages'.
        """
        # A1 sends a message with name, label
        self.t_send = PetriNet.Transition("t_send", "a!")
        # A2 receives the message
        self.t_receive = PetriNet.Transition(
            "t_receive",
            "a?",
        )
        self.net.transitions.add(self.t_send)
        self.net.transitions.add(self.t_receive)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions."""
        petri_utils.add_arc_from_to(self.p_a1_start, self.t_send, self.net)
        petri_utils.add_arc_from_to(self.p_a2_start, self.t_receive, self.net)

        petri_utils.add_arc_from_to(self.t_send, self.p_a, self.net)
        petri_utils.add_arc_from_to(self.p_a, self.t_receive, self.net)

        petri_utils.add_arc_from_to(self.t_send, self.p_a1_end, self.net)
        petri_utils.add_arc_from_to(self.t_receive, self.p_a2_end, self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings."""
        # Start with A1 ready to send
        self.initial_marking[self.p_a1_start] = 1
        self.initial_marking[self.p_a2_start] = 1

        # End when A2 receives the message
        self.final_marking[self.p_a1_end] = 1
        self.final_marking[self.p_a2_end] = 1


class IP2(BaseInterfacePattern):
    """Agent X concurrently sends (recieves) several messages (>1) to (from) an Agent Y."""


class IP3(BaseInterfacePattern):
    """Agent Xsends (recieves) exactly one out of two (or more) alternative message sets to (from) an Agent Y."""


class IP4(BaseInterfacePattern):
    """Agent X sends a message to an Agent Y. Subsequently, Y sends a reposne to X."""


class IP5(BaseInterfacePattern):
    """Agent X concurrently sends several messages (>1) to an Agent Y.
    Then Y sends a reponse for each message recieved from X
    """


class IP6(BaseInterfacePattern):
    """Agent X sends exactly one out of two (or more) alternative message sets to an agent Y.
    Subsequently, Y sends a corresponding response to a message recieved from X.
    """


class IP7(BaseInterfacePattern):
    """Agent X sends exactly one out of two (or more) alternative message sets to an agent Y.
    Subsequently, Y sends a corresponding response to a message recieved from X.
    """


class IP8(BaseInterfacePattern):
    """An Iterative Implementation of IP-4,
    such that the message exchange continues till an Agent X does not need reponses from Agent Y.
    """


class IP9(BaseInterfacePattern):
    """Before exchanging messages, agents X and Y execute a synchronous action."""


class IP10(BaseInterfacePattern):
    """After exchanging messages, agents X and Y execute a synchronous action."""


class IP11(BaseInterfacePattern):
    """Concurrently with message exchange, agents X and Y execute a synchronous action."""


class IP12(BaseInterfacePattern):
    """Agents X and Y either execute a synchronous action r exchange, but not both."""
