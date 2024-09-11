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
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial Marking for A1
            "p2": PetriNet.Place("p2"),  # Final Marking for A1
            "p3": PetriNet.Place("p3"),  # Initial Marking for A2
            "p4": PetriNet.Place("p4"),  # Final Marking for A2
            "pa": PetriNet.Place("pa"),  # Channel A1 - A2
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions t_send (sending message) and t_receive (receiving message).
        'Single labeled transition used to send/recieve messages'.
        'Channels are added only in a single direction to send/recieve messages'.
        """
        # Create transitions
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions."""
        # marks from initial places to transitions
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["a?"], self.net)
        # Interaction arcs A1 -> A2
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        # marks from transitions to final places
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a?"], self.places["p4"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings."""
        # Start with A1 ready to send
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p3"]] = 1

        # End when A2 receives the message
        self.final_marking[self.places["p2"]] = 1
        self.final_marking[self.places["p4"]] = 1


class IP2(BaseInterfacePattern):
    """Agent X concurrently sends (recieves) several messages (>1) to (from) an Agent Y."""

    def __init__(self) -> None:
        """Initializes the IP-2."""
        # Call the superclass constructor
        super().__init__("IP-2")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p9 and pa, pb for IP-2.
        'Multiple places for different states and interactions'.
        """
        # Create places with a consistent naming convention
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial Marking for A1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),
            "p4": PetriNet.Place("p4"),  # Final Marking for A1
            "p5": PetriNet.Place("p5"),  # Final Marking for A1
            "p6": PetriNet.Place("p6"),  # Initial Marking for A2
            "p7": PetriNet.Place("p7"),
            "p8": PetriNet.Place("p8"),
            "p9": PetriNet.Place("p9"),  # Final Marking for A2
            "p10": PetriNet.Place("p10"),  # Final Marking for A2
            "pa": PetriNet.Place("pa"),  # Channel A1 - A2
            "pb": PetriNet.Place("pb"),  # Channel A1 - A2
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-2.
        'Transitions handle various actions and interactions between places'.
        """
        # Create transitions with a consistent naming convention
        self.transitions = {
            "c": PetriNet.Transition("c", "c"),
            "a!": PetriNet.Transition("a!", "a!"),
            "b!": PetriNet.Transition("b!", "b!"),
            "d": PetriNet.Transition("d", "d"),
            "b?": PetriNet.Transition("b?", "b?"),
            "a?": PetriNet.Transition("a?", "a?"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-2."""
        # Define arcs for the left side
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["c"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c"], self.places["p3"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p4"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p5"], self.net)

        # Define arcs for the right side
        petri_utils.add_arc_from_to(self.places["p6"], self.transitions["d"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d"], self.places["p7"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d"], self.places["p8"], self.net)
        petri_utils.add_arc_from_to(self.places["p7"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.places["p9"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p9"], self.net)
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p10"],
            self.net,
        )

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-2."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p6"]] = 1

        self.final_marking[self.places["p4"]] = 1
        self.final_marking[self.places["p5"]] = 1
        self.final_marking[self.places["p9"]] = 1
        self.final_marking[self.places["p10"]] = 1


class IP3(BaseInterfacePattern):
    """Agent Xsends (recieves) exactly one out of two (or more) alternative message sets to (from) an Agent Y."""

    def __init__(self) -> None:
        """Initializes the IP-3."""
        # Call the superclass constructor
        super().__init__("IP-3")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p4 and pa, pb for IP-3."""
        # Create places with a consistent naming convention
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state for Agent 1
            "p2": PetriNet.Place("p2"),  # Final state for Agent 1
            "p3": PetriNet.Place("p3"),  # Initial state for Agent 2
            "p4": PetriNet.Place("p4"),  # Final state for Agent 2
            "pa": PetriNet.Place("pa"),  # Channel A
            "pb": PetriNet.Place("pb"),  # Channel B
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-3."""
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-3."""
        # Define arcs for the left side
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p2"], self.net)

        # Define arcs for the right side
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p4"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a?"], self.places["p4"], self.net)

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-3."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p3"]] = 1

        self.final_marking[self.places["p2"]] = 1
        self.final_marking[self.places["p4"]] = 1


class IP4(BaseInterfacePattern):
    """Agent X sends a message to an Agent Y. Subsequently, Y sends a reposne to X."""

    def __init__(self) -> None:
        """Initializes the IP-4."""
        # Call the superclass constructor
        super().__init__("IP-4")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p4 and pa, pb for IP-4."""
        # Create places with a consistent naming convention
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state for Agent 1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),  # Final state for Agent 1
            "p4": PetriNet.Place("p4"),  # Initial state for Agent 2
            "p5": PetriNet.Place("p5"),
            "p6": PetriNet.Place("p6"),  # Final state for Agent 2
            "pa": PetriNet.Place("pa"),  # Channel A
            "pb": PetriNet.Place("pb"),  # Channel B
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-4.
        'Transitions handle sending and receiving of messages'.
        """
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-4."""
        # Define arcs for the left side
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p3"], self.net)

        # Define arcs for the right side
        petri_utils.add_arc_from_to(self.places["p4"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a?"], self.places["p5"], self.net)
        petri_utils.add_arc_from_to(self.places["p5"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p6"], self.net)

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-4."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p4"]] = 1

        self.final_marking[self.places["p3"]] = 1
        self.final_marking[self.places["p6"]] = 1


class IP5(BaseInterfacePattern):
    """Agent X concurrently sends several messages (>1) to an Agent Y.
    Then Y sends a reponse for each message recieved from X
    """

    def __init__(self) -> None:
        """Initializes the IP-5."""
        # Call the superclass constructor
        super().__init__("IP-5")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p0 to p9 and pa to pd for IP-5."""
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state for Agent 1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),
            "p4": PetriNet.Place("p4"),
            "p5": PetriNet.Place("p5"),
            "p6": PetriNet.Place("p6"),  # Final state for Agent 1
            "p7": PetriNet.Place("p7"),  # Final state for Agent 1
            "p8": PetriNet.Place("p8"),  # Initial state for Agent 2
            "p9": PetriNet.Place("p9"),
            "p10": PetriNet.Place("p10"),
            "p11": PetriNet.Place("p11"),
            "p12": PetriNet.Place("p12"),
            "p13": PetriNet.Place("p13"),  # Final state for Agent 2
            "p14": PetriNet.Place("p14"),  # Final state for Agent 2
            "pa": PetriNet.Place("pa"),  # Channel A
            "pb": PetriNet.Place("pb"),  # Channel B
            "pc": PetriNet.Place("pc"),  # Channel C
            "pd": PetriNet.Place("pd"),  # Channel D
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-5."""
        self.transitions = {
            "e": PetriNet.Transition("e"),
            "f": PetriNet.Transition("f"),
            "a!": PetriNet.Transition("a!"),
            "a?": PetriNet.Transition("a?"),
            "b!": PetriNet.Transition("b!"),
            "b?": PetriNet.Transition("b?"),
            "c!": PetriNet.Transition("c!"),
            "c?": PetriNet.Transition("c?"),
            "d!": PetriNet.Transition("d!"),
            "d?": PetriNet.Transition("d?"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-5."""
        # Define arcs for the left side
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["e"], self.net)
        petri_utils.add_arc_from_to(self.transitions["e"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.transitions["e"], self.places["p3"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p4"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p5"], self.net)
        petri_utils.add_arc_from_to(self.places["p4"], self.transitions["c?"], self.net)
        petri_utils.add_arc_from_to(self.places["p5"], self.transitions["d?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c?"], self.places["p6"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d?"], self.places["p7"], self.net)

        # Define arcs for the right side
        petri_utils.add_arc_from_to(self.places["p8"], self.transitions["f"], self.net)
        petri_utils.add_arc_from_to(self.transitions["f"], self.places["p9"], self.net)
        petri_utils.add_arc_from_to(self.transitions["f"], self.places["p10"], self.net)
        petri_utils.add_arc_from_to(self.places["p9"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(
            self.places["p10"],
            self.transitions["a?"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p11"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p12"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p11"],
            self.transitions["d!"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p12"],
            self.transitions["c!"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["d!"],
            self.places["p13"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["c!"],
            self.places["p14"],
            self.net,
        )

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c!"], self.places["pc"], self.net)
        petri_utils.add_arc_from_to(self.places["pc"], self.transitions["c?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d!"], self.places["pd"], self.net)
        petri_utils.add_arc_from_to(self.places["pd"], self.transitions["d?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-5."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p8"]] = 1

        self.final_marking[self.places["p6"]] = 1
        self.final_marking[self.places["p7"]] = 1
        self.final_marking[self.places["p13"]] = 1
        self.final_marking[self.places["p14"]] = 1


class IP6(BaseInterfacePattern):
    """Agent X sends exactly one out of two (or more) alternative message sets to an agent Y.
    Subsequently, Y sends a corresponding response to a message recieved from X.
    """

    def __init__(self) -> None:
        """Initializes the IP-6."""
        # Call the superclass constructor
        super().__init__("IP-6")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places P1 to P6 and Pa to Pd for IP-6."""
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state for Agent 1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),
            "p4": PetriNet.Place("p4"),  # Final state for Agent 1
            "p5": PetriNet.Place("p5"),  # Initial state for Agent 2
            "p6": PetriNet.Place("p6"),
            "p7": PetriNet.Place("p7"),
            "p8": PetriNet.Place("p8"),  # Final state for Agent 2
            "pa": PetriNet.Place("pa"),  # Channel A
            "pb": PetriNet.Place("pb"),  # Channel B
            "pc": PetriNet.Place("pc"),  # Channel C
            "pd": PetriNet.Place("pd"),  # Channel D
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-6."""
        self.transitions = {
            "a!": PetriNet.Transition("a!"),
            "a?": PetriNet.Transition("a?"),
            "b!": PetriNet.Transition("b!"),
            "b?": PetriNet.Transition("b?"),
            "c!": PetriNet.Transition("c!"),
            "c?": PetriNet.Transition("c?"),
            "d!": PetriNet.Transition("d!"),
            "d?": PetriNet.Transition("d?"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-6."""
        # Define arcs for the left side
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p3"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["c?"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["d?"], self.net)
        petri_utils.add_arc_from_to(
            self.transitions["c?"],
            self.places["p4"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["d?"],
            self.places["p4"],
            self.net,
        )

        # Define arcs for the right side
        petri_utils.add_arc_from_to(self.places["p5"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.places["p5"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p6"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a?"], self.places["p7"], self.net)
        petri_utils.add_arc_from_to(self.places["p6"], self.transitions["d!"], self.net)
        petri_utils.add_arc_from_to(self.places["p7"], self.transitions["c!"], self.net)

        petri_utils.add_arc_from_to(
            self.transitions["d!"],
            self.places["p8"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["c!"],
            self.places["p8"],
            self.net,
        )

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c!"], self.places["pc"], self.net)
        petri_utils.add_arc_from_to(self.places["pc"], self.transitions["c?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d!"], self.places["pd"], self.net)
        petri_utils.add_arc_from_to(self.places["pd"], self.transitions["d?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-6."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p5"]] = 1

        self.final_marking[self.places["p4"]] = 1
        self.final_marking[self.places["p8"]] = 1


class IP7(BaseInterfacePattern):
    """Agent X sends exactly one out of two (or more) alternative message sets to an agent Y.
    Subsequently, Y sends a corresponding response to a message recieved from X.
    """

    def __init__(self) -> None:
        """Initializes the IP-7."""
        # Call the superclass constructor
        super().__init__("IP-7")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p6, pa to pc, and additional places for IP-7."""
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state A1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),
            "p4": PetriNet.Place("p4"),  # Final state A1
            "p5": PetriNet.Place("p5"),  # Initial state A2
            "p6": PetriNet.Place("p6"),
            "p7": PetriNet.Place("p7"),
            "p8": PetriNet.Place("p8"),  # Final state A2
            "pa": PetriNet.Place("pa"),  # Channel A
            "pb": PetriNet.Place("pb"),  # Channel B
            "pc": PetriNet.Place("pc"),  # Channel C
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-7."""
        self.transitions = {
            "d": PetriNet.Transition("d"),
            "a!": PetriNet.Transition("a!"),
            "a?": PetriNet.Transition("a?"),
            "b!": PetriNet.Transition("b!"),
            "b?": PetriNet.Transition("b?"),
            "c!": PetriNet.Transition("c!"),
            "c?": PetriNet.Transition("c?"),
            "e": PetriNet.Transition("e"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-7."""
        # Define arcs for the left side
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["d"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p3"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a?"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["c!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c!"], self.places["p4"], self.net)

        # Define arcs for the right side
        petri_utils.add_arc_from_to(self.places["p5"], self.transitions["e"], self.net)
        petri_utils.add_arc_from_to(self.transitions["e"], self.places["p6"], self.net)
        petri_utils.add_arc_from_to(self.places["p6"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p7"], self.net)
        petri_utils.add_arc_from_to(self.places["p7"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p6"], self.net)
        petri_utils.add_arc_from_to(self.places["p6"], self.transitions["c?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c?"], self.places["p8"], self.net)

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c!"], self.places["pc"], self.net)
        petri_utils.add_arc_from_to(self.places["pc"], self.transitions["c?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-7."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p5"]] = 1

        self.final_marking[self.places["p4"]] = 1
        self.final_marking[self.places["p8"]] = 1


class IP8(BaseInterfacePattern):
    """An Iterative Implementation of IP-4,
    such that the message exchange continues till an Agent X does not need reponses from Agent Y.
    """

    def __init__(self) -> None:
        """Initializes the IP-8."""
        # Call the superclass constructor
        super().__init__("IP-8")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p15, pa to pc, and additional places for IP-8."""
        self.places = {f"p{i}": PetriNet.Place(f"p{i}") for i in range(1, 18)}
        self.places.update(
            {
                "pa": PetriNet.Place("pa"),  # Channel A
                "pb": PetriNet.Place("pb"),  # Channel B
                "packA": PetriNet.Place("packA"),  # Acknowledgements
                "packB": PetriNet.Place("packB"),
                "paR": PetriNet.Place("paR"),
                "pbR": PetriNet.Place("pbR"),
            },
        )
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-8."""
        self.transitions = {
            "a!": PetriNet.Transition("a!"),
            "a?_1": PetriNet.Transition("a?_1"),
            "a?_2": PetriNet.Transition("a?_2"),
            "b!": PetriNet.Transition("b!"),
            "b?_1": PetriNet.Transition("b?_1"),
            "b?_2": PetriNet.Transition("b?_2"),
            "ackA!": PetriNet.Transition("ackA!"),
            "ackA?": PetriNet.Transition("ackA?"),
            "ackB?": PetriNet.Transition("ackB?"),
            "ackB!": PetriNet.Transition("ackB!"),
            "aR?": PetriNet.Transition("aR?"),
            "aR!": PetriNet.Transition("aR!"),
            "bR?": PetriNet.Transition("bR?"),
            "bR!": PetriNet.Transition("bR!"),
            "c": PetriNet.Transition("c"),
            "d": PetriNet.Transition("d"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:  # noqa: PLR0915
        """Defines the arcs connecting places and transitions for IP-8."""
        # Define arcs for the left part
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(
            self.places["p2"],
            self.transitions["bR?"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p2"],
            self.transitions["ackA?"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["bR?"],
            self.places["p3"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p3"],
            self.transitions["a?_2"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?_2"],
            self.places["p4"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["ackA?"],
            self.places["p4"],
            self.net,
        )

        # Define arcs for the center part
        petri_utils.add_arc_from_to(
            self.places["p5"],
            self.transitions["a?_1"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p5"],
            self.transitions["b?_1"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?_1"],
            self.places["p6"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?_1"],
            self.places["p7"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p6"],
            self.transitions["aR!"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p7"],
            self.transitions["ackA!"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?_1"],
            self.places["p8"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p8"],
            self.transitions["ackB!"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?_1"],
            self.places["p9"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p9"],
            self.transitions["bR!"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["aR!"],
            self.places["p10"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["ackA!"],
            self.places["p11"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["ackB!"],
            self.places["p12"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["bR!"],
            self.places["p13"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p10"],
            self.transitions["d"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p11"],
            self.transitions["d"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p12"],
            self.transitions["e"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p13"],
            self.transitions["d"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["e"],
            self.places["p14"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["d"],
            self.transitions["p14"],
            self.net,
        )

        # Define arcs for the right part
        petri_utils.add_arc_from_to(
            self.places["p15"],
            self.transitions["b!"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p16"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p16"],
            self.transitions["aR?"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p16"],
            self.transitions["ackB?"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["aR?"],
            self.places["p17"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p17"],
            self.transitions["b?_2"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?_2"],
            self.places["p18"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["ackB?"],
            self.places["p18"],
            self.net,
        )

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(
            self.places["pa"],
            self.transitions["a?_1"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["pa"],
            self.transitions["a?_2"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["pb"],
            self.transitions["b?_1"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["pb"],
            self.transitions["b?_2"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["bR!"],
            self.places["pbR"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["pbR"],
            self.transitions["bR?"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["aR!"],
            self.places["paR"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["paR"],
            self.transitions["aR?"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["ackA!"],
            self.places["packA"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["packA"],
            self.transitions["ackA?"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["ackB!"],
            self.places["packB"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["packB"],
            self.transitions["ackB?"],
            self.net,
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-8."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p5"]] = 1
        self.initial_marking[self.places["p15"]] = 1

        self.final_marking[self.places["p4"]] = 1
        self.final_marking[self.places["p14"]] = 1
        self.final_marking[self.places["p18"]] = 1


class IP9(BaseInterfacePattern):
    """Before exchanging messages, agents X and Y execute a synchronous action."""

    def __init__(self) -> None:
        """Initializes the IP-9."""
        # Call the superclass constructor
        super().__init__("IP-9")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p6, a1, a2, pa, and pb for IP-9."""
        # Create places with a consistent naming convention
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state for Agent 1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),
            "p4": PetriNet.Place("p4"),  # Final state for Agent 1
            "p5": PetriNet.Place("p5"),  #  Initial state for Agent 2
            "p6": PetriNet.Place("p6"),
            "p7": PetriNet.Place("p7"),
            "p8": PetriNet.Place("p8"),  # Final state for Agent 2
            "pa": PetriNet.Place("pa"),  # Channel A
            "pb": PetriNet.Place("pb"),  # Channel B
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-9.
        'Transitions handle sending and receiving of messages and responses'.
        """
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "s": PetriNet.Transition("s", "s"),  # Synchronization transition
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-9."""
        # Define arcs for the left part
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["s"], self.net)
        petri_utils.add_arc_from_to(self.transitions["s"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p3"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p4"], self.net)

        # Define arcs for the right part
        petri_utils.add_arc_from_to(self.places["p5"], self.transitions["s"], self.net)
        petri_utils.add_arc_from_to(self.transitions["s"], self.places["p6"], self.net)
        petri_utils.add_arc_from_to(self.places["p6"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a?"], self.places["p7"], self.net)
        petri_utils.add_arc_from_to(self.places["p7"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p8"], self.net)

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-9."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p5"]] = 1

        self.final_marking[self.places["p4"]] = 1
        self.final_marking[self.places["p8"]] = 1


class IP10(BaseInterfacePattern):
    """After exchanging messages, agents X and Y execute a synchronous action."""

    def __init__(self) -> None:
        """Initializes the IP-10."""
        # Call the superclass constructor
        super().__init__("IP-10")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p6, a1, a2, a, and b for IP-10."""
        # Create places with a consistent naming convention
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state for Agent 1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),
            "p4": PetriNet.Place("p4"),  # Final state for Agent 1
            "p5": PetriNet.Place("p5"),  # Initial state for Agent 2
            "p6": PetriNet.Place("p6"),
            "p7": PetriNet.Place("p7"),
            "p8": PetriNet.Place("p8"),  # Final state for Agent 2, Optional
            "pa": PetriNet.Place("pa"),  # Channel A
            "pb": PetriNet.Place("pb"),  # Channel B
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-10."""
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "s?": PetriNet.Transition("s?", "s?"),  # Synchronization transition
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-10."""
        # Define arcs for the left part
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p3"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["s"], self.net)
        petri_utils.add_arc_from_to(self.transitions["s"], self.places["p4"], self.net)

        # Define arcs for the right part
        petri_utils.add_arc_from_to(
            self.places["p5"],
            self.transitions["a?!"],
            self.net,
        )
        petri_utils.add_arc_from_to(self.transitions["a?"], self.places["p6"], self.net)
        petri_utils.add_arc_from_to(self.places["p6"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p7"], self.net)
        petri_utils.add_arc_from_to(self.places["p7"], self.transitions["s"], self.net)
        petri_utils.add_arc_from_to(self.transitions["s"], self.places["p8"], self.net)

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-10."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p5"]] = 1

        self.final_marking[self.places["p4"]] = 1
        self.final_marking[self.places["p8"]] = 1  # Optional


class IP11(BaseInterfacePattern):
    """Concurrently with message exchange, agents X and Y execute a synchronous action."""

    def __init__(self) -> None:
        """Initializes the IP-11."""
        # Call the superclass constructor
        super().__init__("IP-11")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p7 and a, b for IP-11."""
        # Create places with a consistent naming convention
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state for Agent 1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),
            "p4": PetriNet.Place("p4"),
            "p5": PetriNet.Place("p5"),
            "p6": PetriNet.Place("p6"),  # Final state for Agent 1
            "p7": PetriNet.Place("p7"),  # Initial state for Agent 2
            "p8": PetriNet.Place("p8"),
            "p9": PetriNet.Place("p9"),
            "p10": PetriNet.Place("p10"),
            "p11": PetriNet.Place("p11"),
            "p12": PetriNet.Place("p12"),  # Final state for Agent 2
            "pa": PetriNet.Place("pa"),
            "pb": PetriNet.Place("pb"),
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-11.
        'Transitions handle the message exchanges between agents'.
        """
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "s": PetriNet.Transition("s", "s"),
            "c": PetriNet.Transition("c", "c"),
            "d": PetriNet.Transition("d", "d"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-11."""
        # Define arcs for left side
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["c"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c"], self.places["p3"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["s"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p4"], self.net)
        petri_utils.add_arc_from_to(self.transitions["s"], self.places["p5"], self.net)
        petri_utils.add_arc_from_to(self.places["p4"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p6"], self.net)

        # Define arcs for right side
        petri_utils.add_arc_from_to(self.places["p7"], self.transitions["d"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d"], self.places["p8"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d"], self.places["p9"], self.net)
        petri_utils.add_arc_from_to(self.places["p8"], self.transitions["s"], self.net)
        petri_utils.add_arc_from_to(self.places["p9"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["s"], self.places["p10"], self.net)
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p11"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.places["p11"],
            self.transitions["b!"],
            self.net,
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p12"],
            self.net,
        )

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-11."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p7"]] = 1

        self.final_marking[self.places["p6"]] = 1
        self.initial_marking[self.places["p12"]] = 1


class IP12(BaseInterfacePattern):
    """Agents X and Y either execute a synchronous action r exchange, but not both."""

    def __init__(self) -> None:
        """Initializes the IP-12."""
        # Call the superclass constructor
        super().__init__("IP-12")

        # Define the places, transitions, arcs, and markings
        self._define_places()
        self._define_transitions()
        self._define_arcs()
        self._define_markings()

    def _define_places(self) -> None:
        """Defines places p1 to p6, a, b, A1, and A2 for IP-12."""
        # Create places with a consistent naming convention
        self.places = {
            "p1": PetriNet.Place("p1"),  # Initial state for Agent 1
            "p2": PetriNet.Place("p2"),
            "p3": PetriNet.Place("p3"),
            "p4": PetriNet.Place("p4"),  # Final state for Agent 1
            "p5": PetriNet.Place("p5"),  # Initial state for Agent 2
            "p6": PetriNet.Place("p6"),
            "p7": PetriNet.Place("p7"),
            "p8": PetriNet.Place("p8"),  # Final state for Agent 2
            "pa": PetriNet.Place("pa"),
            "pb": PetriNet.Place("pb"),
        }
        for place in self.places.values():
            self.net.places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-12.
        'Transitions handle the message exchanges and intermediate steps'.
        """
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "s": PetriNet.Transition("s", "s"),
            "c": PetriNet.Transition("c", "c"),
            "d": PetriNet.Transition("d", "d"),
        }
        for transition in self.transitions.values():
            self.net.transitions.add(transition)

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-12."""
        # Define arcs for left side
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["a!"], self.net)
        petri_utils.add_arc_from_to(self.places["p1"], self.transitions["s"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["p2"], self.net)
        petri_utils.add_arc_from_to(self.transitions["s"], self.places["p3"], self.net)
        petri_utils.add_arc_from_to(self.places["p2"], self.transitions["b?"], self.net)
        petri_utils.add_arc_from_to(self.places["p3"], self.transitions["c"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b?"], self.places["p4"], self.net)
        petri_utils.add_arc_from_to(self.transitions["c"], self.places["p4"], self.net)

        # Define arcs for right side
        petri_utils.add_arc_from_to(self.places["p5"], self.transitions["s"], self.net)
        petri_utils.add_arc_from_to(self.places["p5"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["s"], self.places["p6"], self.net)
        petri_utils.add_arc_from_to(self.transitions["a?"], self.places["p7"], self.net)
        petri_utils.add_arc_from_to(self.places["p6"], self.transitions["d"], self.net)
        petri_utils.add_arc_from_to(self.places["p7"], self.transitions["b!"], self.net)
        petri_utils.add_arc_from_to(self.transitions["d"], self.places["p8"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["p8"], self.net)

        # Define interaction arcs
        petri_utils.add_arc_from_to(self.transitions["a!"], self.places["pa"], self.net)
        petri_utils.add_arc_from_to(self.places["pa"], self.transitions["a?"], self.net)
        petri_utils.add_arc_from_to(self.transitions["b!"], self.places["pb"], self.net)
        petri_utils.add_arc_from_to(self.places["pb"], self.transitions["b?"], self.net)

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-12."""
        # Set initial and final markings
        self.initial_marking[self.places["p1"]] = 1
        self.initial_marking[self.places["p5"]] = 1

        self.final_marking[self.places["p4"]] = 1
        self.final_marking[self.places["p8"]] = 1
