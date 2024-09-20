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

    def __init__(self, name: str, num_agents: int) -> None:
        """
        Initializes the Petri net and markings.

        Args:
            name (str): The name of the Petri net.
            num_agents (int): The number of agents involved in the interface pattern.
        """
        # copy values for later usage
        self.name = name
        self.num_agents = num_agents

        # empty dicts to store the nets  and markings
        self.nets = {}
        self.initial_markings = {}
        self.final_markings = {}
        # create Nets A1,...,An
        for i in range(1, self.num_agents + 1):
            self.nets[f"A{i}"] = PetriNet(f"A{i}")
            self.initial_markings[f"A{i}"] = Marking()
            self.final_markings[f"A{i}"] = Marking()

        # define the places and transitions for all nets
        self._define_places()
        self._define_transitions()

        # define arcs for all subnets
        self._define_arcs()

        # define the markings in all nets
        self._define_markings()

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

    def get_nets(self) -> list[PetriNet]:
        """
        Returns the individual nets of Agent1, Agent2, and the total combined net.

        Returns:
            tuple: (agent1_net, agent2_net, total_net)
        """
        return self.nets

    def get_markings(self) -> tuple[Marking, Marking]:
        """
        Returns the initial and final markings for the individual nets of Agent1 and Agent2.

        Returns:
            tuple: (initial_marking, final_marking)
        """
        return self.initial_markings, self.final_markings

    def get_net(self, net_name: str) -> tuple:
        """
        Returns the Petri net along with its initial and final markings.

        Args:
            net_name (str): The name of the Petri net.

        Returns:
            tuple: (net, initial_marking, final_marking)
        """
        if net_name not in self.nets:
            msg = f"Net {net_name} not found in the interface pattern"
            raise ValueError(msg)
        # get the net
        net = self.nets[net_name]
        initial_marking = self.initial_markings[net_name]
        final_marking = self.final_markings[net_name]
        return net, initial_marking, final_marking


class IP1(BaseInterfacePattern):
    """Defines the IP-1 interface pattern, involving Agent A1 sending a message and Agent A2 receiving it."""

    def __init__(self) -> None:
        """Initializes the IP-1."""
        # Call the superclass constructor
        super().__init__("IP1", 2)

    def _define_places(self) -> None:
        """Defines places p_A1 (Agent A1) and p_A2 (Agent A2).
        'Two Agents A1 and A2'.
        """
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

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
        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A2"].transitions.add(self.transitions["a?"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions."""
        # arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_2"]] = 1
        self.final_markings["A2"][self.places["p_A2_2"]] = 1


class IP2(BaseInterfacePattern):
    """Agent X concurrently sends (recieves) several messages (>1) to (from) an Agent Y."""

    def __init__(self) -> None:
        """Initializes the IP-2."""
        # Call the superclass constructor
        super().__init__("IP-2", 2)

    def _define_places(self) -> None:
        """Defines places p1 to p9 and pa, pb for IP-2.
        'Multiple places for different states and interactions'.
        """
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),  # Final Marking for A1
            "p_A1_5": PetriNet.Place("p_A1_5"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),  # Final Marking for A2
            "p_A2_5": PetriNet.Place("p_A2_5"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-2.
        'Transitions handle various actions and interactions between places'.
        """
        # Create transitions
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "c": PetriNet.Transition("c", "c"),
            "d": PetriNet.Transition("d", "d"),
        }
        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["b!"])
        self.nets["A1"].transitions.add(self.transitions["c"])
        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b?"])
        self.nets["A2"].transitions.add(self.transitions["d"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-2."""
        # arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["c"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["b!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A1_5"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["d"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["b?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_3"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_5"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-2."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_4"]] = 1
        self.final_markings["A1"][self.places["p_A1_5"]] = 1
        self.final_markings["A2"][self.places["p_A2_4"]] = 1
        self.final_markings["A2"][self.places["p_A2_5"]] = 1


class IP3(BaseInterfacePattern):
    """Agent Xsends (recieves) exactly one out of two (or more) alternative message sets to (from) an Agent Y."""

    def __init__(self) -> None:
        """Initializes the IP-3."""
        # Call the superclass constructor
        super().__init__("IP-3", 2)

    def _define_places(self) -> None:
        """Defines places p1 to p4 and pa, pb for IP-3."""
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-3."""
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
        }
        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["b!"])
        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b?"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-3."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["b!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["b?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-3."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_2"]] = 1
        self.final_markings["A2"][self.places["p_A2_2"]] = 1


class IP4(BaseInterfacePattern):
    """Agent X sends a message to an Agent Y. Subsequently, Y sends a reposne to X."""

    def __init__(self) -> None:
        """Initializes the IP-4."""
        # Call the superclass constructor
        super().__init__("IP-4", 2)

    def _define_places(self) -> None:
        """Defines places p1 to p4 and pa, pb for IP-4."""
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

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

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["b?"])
        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b!"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-4."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["b?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["b!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-4."""
        # Set initial and final markings
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        self.final_markings["A1"][self.places["p_A1_3"]] = 1
        self.final_markings["A2"][self.places["p_A2_3"]] = 1


class IP5(BaseInterfacePattern):
    """Agent X concurrently sends several messages (>1) to an Agent Y.
    Then Y sends a reponse for each message recieved from X
    """

    def __init__(self) -> None:
        """Initializes the IP-5."""
        # Call the superclass constructor
        super().__init__("IP-5", 2)

    def _define_places(self) -> None:
        """Defines places p0 to p9 and pa to pd for IP-5."""
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),
            "p_A1_5": PetriNet.Place("p_A1_5"),
            "p_A1_6": PetriNet.Place("p_A1_6"),  # Final Marking for A1
            "p_A1_7": PetriNet.Place("p_A1_7"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),
            "p_A2_5": PetriNet.Place("p_A2_5"),
            "p_A2_6": PetriNet.Place("p_A2_6"),  # Final Marking for A2
            "p_A2_7": PetriNet.Place("p_A2_7"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-5."""
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "c!": PetriNet.Transition("c!", "c!"),
            "c?": PetriNet.Transition("c?", "c?"),
            "d!": PetriNet.Transition("d!", "d!"),
            "d?": PetriNet.Transition("d?", "d?"),
            "e": PetriNet.Transition("e", "e"),
            "f": PetriNet.Transition("f", "f"),
        }

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["b!"])
        self.nets["A1"].transitions.add(self.transitions["c?"])
        self.nets["A1"].transitions.add(self.transitions["d?"])
        self.nets["A1"].transitions.add(self.transitions["e"])

        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b?"])
        self.nets["A2"].transitions.add(self.transitions["c!"])
        self.nets["A2"].transitions.add(self.transitions["d!"])
        self.nets["A2"].transitions.add(self.transitions["f"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-5."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["e"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["e"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["e"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["b!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A1_5"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_4"],
            self.transitions["c?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_5"],
            self.transitions["d?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c?"],
            self.places["p_A1_6"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d?"],
            self.places["p_A1_7"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["f"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["f"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["f"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["b?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_3"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_5"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_4"],
            self.transitions["d!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_5"],
            self.transitions["c!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d!"],
            self.places["p_A2_6"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c!"],
            self.places["p_A2_7"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-5."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_6"]] = 1
        self.final_markings["A1"][self.places["p_A1_7"]] = 1
        self.final_markings["A2"][self.places["p_A2_6"]] = 1
        self.final_markings["A2"][self.places["p_A2_7"]] = 1


class IP6(BaseInterfacePattern):
    """Agent X sends exactly one out of two (or more) alternative message sets to an agent Y.
    Subsequently, Y sends a corresponding response to a message recieved from X.
    """

    def __init__(self) -> None:
        """Initializes the IP-6."""
        # Call the superclass constructor
        super().__init__("IP-6", 2)

    def _define_places(self) -> None:
        """Defines places P1 to P6 and Pa to Pd for IP-6."""
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-6."""
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "c!": PetriNet.Transition("c!", "c!"),
            "c?": PetriNet.Transition("c?", "c?"),
            "d!": PetriNet.Transition("d!", "d!"),
            "d?": PetriNet.Transition("d?", "d?"),
        }

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["b!"])
        self.nets["A1"].transitions.add(self.transitions["c?"])
        self.nets["A1"].transitions.add(self.transitions["d?"])

        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b?"])
        self.nets["A2"].transitions.add(self.transitions["c!"])
        self.nets["A2"].transitions.add(self.transitions["d!"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-6."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["b!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["c?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["d?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c?"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d?"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["b?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["d!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_3"],
            self.transitions["c!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d!"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c!"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-6."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_4"]] = 1
        self.final_markings["A2"][self.places["p_A2_4"]] = 1


class IP7(BaseInterfacePattern):
    """Agent X sends exactly one out of two (or more) alternative message sets to an agent Y.
    Subsequently, Y sends a corresponding response to a message recieved from X.
    """

    def __init__(self) -> None:
        """Initializes the IP-7."""
        # Call the superclass constructor
        super().__init__("IP-7", 2)

    def _define_places(self) -> None:
        """Defines places p1 to p6, pa to pc, and additional places for IP-7."""
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-7."""
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "c!": PetriNet.Transition("c!", "c!"),
            "c?": PetriNet.Transition("c?", "c?"),
            "d": PetriNet.Transition("d", "d"),
            "e": PetriNet.Transition("e", "e"),
        }

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a?"])
        self.nets["A1"].transitions.add(self.transitions["b!"])
        self.nets["A1"].transitions.add(self.transitions["c!"])
        self.nets["A1"].transitions.add(self.transitions["d"])

        self.nets["A2"].transitions.add(self.transitions["a!"])
        self.nets["A2"].transitions.add(self.transitions["b?"])
        self.nets["A2"].transitions.add(self.transitions["c?"])
        self.nets["A2"].transitions.add(self.transitions["e"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-7."""
        # define Arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["d"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["b!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["a?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["c!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c!"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["e"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["e"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["a!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_3"],
            self.transitions["b?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["c?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c?"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-7."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_4"]] = 1
        self.final_markings["A2"][self.places["p_A2_4"]] = 1


class IP8(BaseInterfacePattern):
    """An Iterative Implementation of IP-4,
    such that the message exchange continues till an Agent X does not need reponses from Agent Y.
    """

    def __init__(self) -> None:
        """Initializes the IP-8."""
        # Call the superclass constructor
        super().__init__("IP-8", 3)

    def _define_places(self) -> None:
        """Defines places p1 to p15, pa to pc, and additional places for IP-8."""
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),  # Final Marking for A2
            "p_A3_1": PetriNet.Place("p_A3_1"),  # Initial Marking for A2
            "p_A3_2": PetriNet.Place("p_A3_2"),
            "p_A3_3": PetriNet.Place("p_A3_3"),
            "p_A3_4": PetriNet.Place("p_A3_4"),
            "p_A3_5": PetriNet.Place("p_A3_5"),
            "p_A3_6": PetriNet.Place("p_A3_6"),
            "p_A3_7": PetriNet.Place("p_A3_7"),
            "p_A3_8": PetriNet.Place("p_A3_8"),
            "p_A3_9": PetriNet.Place("p_A3_9"),
            "p_A3_10": PetriNet.Place("p_A3_10"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)
            elif "p_A3" in index:
                self.nets["A3"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-8."""
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "ackA!": PetriNet.Transition("ackA!", "ackA!"),
            "ackA?": PetriNet.Transition("ackA?", "ackA?"),
            "ackB?": PetriNet.Transition("ackB?", "ackB?"),
            "ackB!": PetriNet.Transition("ackB!", "ackB!"),
            "aR?": PetriNet.Transition("aR?", "aR?"),
            "aR!": PetriNet.Transition("aR!", "aR!"),
            "bR?": PetriNet.Transition("bR?", "bR?"),
            "bR!": PetriNet.Transition("bR!", "bR!"),
            "c": PetriNet.Transition("c", "c"),
            "d": PetriNet.Transition("d", "d"),
        }

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["a?"])
        self.nets["A1"].transitions.add(self.transitions["ackA?"])
        self.nets["A1"].transitions.add(self.transitions["bR?"])

        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b?"])
        self.nets["A3"].transitions.add(self.transitions["aR!"])
        self.nets["A3"].transitions.add(self.transitions["ackA!"])
        self.nets["A3"].transitions.add(self.transitions["ackB!"])
        self.nets["A3"].transitions.add(self.transitions["bR!"])
        self.nets["A3"].transitions.add(self.transitions["c"])
        self.nets["A3"].transitions.add(self.transitions["d"])

        self.nets["A3"].transitions.add(self.transitions["b!"])
        self.nets["A3"].transitions.add(self.transitions["aR?"])
        self.nets["A3"].transitions.add(self.transitions["ackB?"])
        self.nets["A3"].transitions.add(self.transitions["b?"])

    def _define_arcs(self) -> None:  # noqa: PLR0915
        """Defines the arcs connecting places and transitions for IP-8."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["ackA?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["bR?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["ackA?"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["bR?"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["a?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )

        # define arcs for A2

        # define arcs for A3

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-8."""



class IP9(BaseInterfacePattern):
    """Before exchanging messages, agents X and Y execute a synchronous action."""

    def __init__(self) -> None:
        """Initializes the IP-9."""
        # Call the superclass constructor
        super().__init__("IP-9", 2)

    def _define_places(self) -> None:
        """Defines places p1 to p6, a1, a2, pa, and pb for IP-9."""
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

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
            "s": PetriNet.Transition("s", "s"),
        }

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["b?"])
        self.nets["A1"].transitions.add(self.transitions["s"])

        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b!"])
        self.nets["A2"].transitions.add(self.transitions["s"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-9."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["s"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["s"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["b?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["s"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["s"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_3"],
            self.transitions["b!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-9."""
        # Set initial and final markings
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        self.final_markings["A1"][self.places["p_A1_4"]] = 1
        self.final_markings["A2"][self.places["p_A2_4"]] = 1


class IP10(BaseInterfacePattern):
    """After exchanging messages, agents X and Y execute a synchronous action."""

    def __init__(self) -> None:
        """Initializes the IP-10."""
        # Call the superclass constructor
        super().__init__("IP-10", 2)

    def _define_places(self) -> None:
        """Defines places p1 to p6, a1, a2, a, and b for IP-10."""
        # naming convention vor places: p1, p2 -> from top to bottom, from left to right
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-10."""
        # Create transitions with a consistent naming convention
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "s": PetriNet.Transition("s", "s"),
        }

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["b?"])
        self.nets["A1"].transitions.add(self.transitions["s"])
        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b!"])
        self.nets["A2"].transitions.add(self.transitions["s"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-10."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["b?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["s"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["s"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["b!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_3"],
            self.transitions["s"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["s"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-10."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_4"]] = 1
        self.final_markings["A2"][self.places["p_A2_4"]] = 1


class IP11(BaseInterfacePattern):
    """Concurrently with message exchange, agents X and Y execute a synchronous action."""

    def __init__(self) -> None:
        """Initializes the IP-11."""
        # Call the superclass constructor
        super().__init__("IP-11", 2)

    def _define_places(self) -> None:
        """Defines places p1 to p7 and a, b for IP-11."""
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),
            "p_A1_5": PetriNet.Place("p_A1_5"),
            "p_A1_6": PetriNet.Place("p_A1_6"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),
            "p_A2_5": PetriNet.Place("p_A2_5"),
            "p_A2_6": PetriNet.Place("p_A2_6"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-11.
        'Transitions handle the message exchanges between agents'.
        """
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "c": PetriNet.Transition("c", "c"),
            "d": PetriNet.Transition("d", "d"),
            "s": PetriNet.Transition("s", "s"),
        }

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a?"])
        self.nets["A1"].transitions.add(self.transitions["b!"])
        self.nets["A1"].transitions.add(self.transitions["c"])
        self.nets["A1"].transitions.add(self.transitions["s"])

        self.nets["A2"].transitions.add(self.transitions["a!"])
        self.nets["A2"].transitions.add(self.transitions["b?"])
        self.nets["A2"].transitions.add(self.transitions["d"])
        self.nets["A2"].transitions.add(self.transitions["s"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-11."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["c"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["s"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["s"],
            self.places["p_A1_5"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_4"],
            self.transitions["b?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A1_6"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["d"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d"],
            self.places["p_A2_2"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["s"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["s"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_3"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_5"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_5"],
            self.transitions["b!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A2_6"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-11."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_6"]] = 1
        self.final_markings["A2"][self.places["p_A2_6"]] = 1


class IP12(BaseInterfacePattern):
    """Agents X and Y either execute a synchronous action r exchange, but not both."""

    def __init__(self) -> None:
        """Initializes the IP-12."""
        # Call the superclass constructor
        super().__init__("IP-12", 2)

    def _define_places(self) -> None:
        """Defines places p1 to p6, a, b, A1, and A2 for IP-12."""
        # Create places
        self.places = {
            "p_A1_1": PetriNet.Place("p_A1_1"),  # Initial Marking for A1
            "p_A1_2": PetriNet.Place("p_A1_2"),
            "p_A1_3": PetriNet.Place("p_A1_3"),
            "p_A1_4": PetriNet.Place("p_A1_4"),  # Final Marking for A1
            "p_A2_1": PetriNet.Place("p_A2_1"),  # Initial Marking for A2
            "p_A2_2": PetriNet.Place("p_A2_2"),
            "p_A2_3": PetriNet.Place("p_A2_3"),
            "p_A2_4": PetriNet.Place("p_A2_4"),  # Final Marking for A2
        }
        for index, place in self.places.items():
            if "p_A1" in index:
                self.nets["A1"].places.add(place)
            elif "p_A2" in index:
                self.nets["A2"].places.add(place)

    def _define_transitions(self) -> None:
        """Defines transitions for IP-12.
        'Transitions handle the message exchanges and intermediate steps'.
        """
        self.transitions = {
            "a!": PetriNet.Transition("a!", "a!"),
            "a?": PetriNet.Transition("a?", "a?"),
            "b!": PetriNet.Transition("b!", "b!"),
            "b?": PetriNet.Transition("b?", "b?"),
            "c": PetriNet.Transition("c", "c"),
            "d": PetriNet.Transition("d", "d"),
            "s": PetriNet.Transition("s", "s"),
        }

        # add transitions to the nets
        self.nets["A1"].transitions.add(self.transitions["a!"])
        self.nets["A1"].transitions.add(self.transitions["b?"])
        self.nets["A1"].transitions.add(self.transitions["c"])
        self.nets["A1"].transitions.add(self.transitions["s"])

        self.nets["A2"].transitions.add(self.transitions["a?"])
        self.nets["A2"].transitions.add(self.transitions["b!"])
        self.nets["A2"].transitions.add(self.transitions["d"])
        self.nets["A2"].transitions.add(self.transitions["s"])

    def _define_arcs(self) -> None:
        """Defines the arcs connecting places and transitions for IP-12."""
        # define arcs for A1
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["a!"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_1"],
            self.transitions["s"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a!"],
            self.places["p_A1_2"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["s"],
            self.places["p_A1_3"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_2"],
            self.transitions["b?"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A1_3"],
            self.transitions["c"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b?"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["c"],
            self.places["p_A1_4"],
            self.nets["A1"],
        )

        # define arcs for A2
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["s"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_1"],
            self.transitions["a?"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["s"],
            self.places["p_A2_2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["a?"],
            self.places["p_A2_3"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_2"],
            self.transitions["d"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.places["p_A2_3"],
            self.transitions["b!"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["d"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )
        petri_utils.add_arc_from_to(
            self.transitions["b!"],
            self.places["p_A2_4"],
            self.nets["A2"],
        )

    def _define_markings(self) -> None:
        """Defines the initial and final markings for IP-12."""
        # initial marking for A1 and A2
        self.initial_markings["A1"][self.places["p_A1_1"]] = 1
        self.initial_markings["A2"][self.places["p_A2_1"]] = 1

        # final markings for A1 and A2
        self.final_markings["A1"][self.places["p_A1_4"]] = 1
        self.final_markings["A2"][self.places["p_A2_4"]] = 1


# List of supported interface patterns
INTERFACE_PATTERNS: list[BaseInterfacePattern] = [
    IP1(),
    IP2,
    IP3,
    IP4,
    IP5,
    IP6,
    IP7,
    IP8,
    IP9,
    IP10,
    IP11,
    IP12,
]

# Control the public API of the module
__all__ = ["INTERFACE_PATTERNS"]
