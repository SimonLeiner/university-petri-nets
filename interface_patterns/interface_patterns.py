"""This module contains the Interface Patterns."""

from abc import ABCMeta
from abc import abstractmethod

from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils import petri_utils


class InterfacePattern(metaclass=ABCMeta):
    """Base Class for Interface Patterns."""

    def __repr__(self) -> str:
        """String representation of the InterfacePattern object."""
        return f"<{self.__class__.__name__}>"

    @abstractmethod
    def send_message() -> None:
        raise NotImplementedError

    @abstractmethod
    def recieve_message() -> None:
        raise NotImplementedError


class AsyncInterfacePattern(InterfacePattern):
    """Base Class for asynchronous interface patterns."""


class SyncInterfacePattern(InterfacePattern):
    """Base Class for synchronous interface patterns."""


class MixedInterfacePattern(InterfacePattern):
    """Base Class for mixed interface patterns. Combine asynchronous and synchronous agent interactions."""


class BilateralPattern(AsyncInterfacePattern):
    """Base Class for Bilateral Interface Patterns. Distinguished by the number of interacting Parties.
    Contain different message exchange variations involving one channel to send a message
    and the other to send an acknowledgement.
    """


class MultilateralPattern(AsyncInterfacePattern):
    """Base Class for Multilateral Interface Patterns IP-8."""


class SingleTransmissionPattern(AsyncInterfacePattern):
    """Base Class for Single Transmission Interface Patterns IP-1, IP-2, IP-3.
    Channels are only in a single way to send/recieve messages. No Acknowledges.
    The number of transmissions specifies how many times interacting agents can exchange messages.
    Describe primitive agent interactions since a sending agent is not supposed to recieve an acknowledgement from the other agent.
    """


class MultipleTransmissionPattern(AsyncInterfacePattern):
    """Base Class for Multiple Transmission Interface Patterns IP-7.
    One Agent can decide to stop the exchange by sending a corresponding message to the other Agent.
    Classified according to the way agetns interact.
    """


class IP1(SingleTransmissionPattern):
    """Agent X sends (recieves) a message to (from) an Agent Y."""


class IP2(SingleTransmissionPattern):
    """Agent X concurrently sends (recieves) several messages (>1) to (from) an Agent Y."""


class IP3(SingleTransmissionPattern):
    """Agent Xsends (recieves) exactly one out of two (or more) alternative message sets to (from) an Agent Y."""


class IP4(BilateralPattern):
    """Agent X sends a message to an Agent Y. Subsequently, Y sends a reposne to X."""


class IP5(BilateralPattern):
    """Agent X concurrently sends several messages (>1) to an Agent Y.
    Then Y sends a reponse for each message recieved from X
    """


class IP6(BilateralPattern):
    """Agent X sends exactly one out of two (or more) alternative message sets to an agent Y.
    Subsequently, Y sends a corresponding response to a message recieved from X.
    """


class IP7(MultipleTransmissionPattern):
    """Agent X sends exactly one out of two (or more) alternative message sets to an agent Y.
    Subsequently, Y sends a corresponding response to a message recieved from X.
    """


class IP8(MultilateralPattern):
    """An Iterative Implementation of IP-4,
    such that the message exchange continues till an Agent X does not need reponses from Agent Y.
    """


class IP9(IP4):
    """Before exchanging messages, agents X and Y execute a synchronous action."""


class IP10(IP4):
    """After exchanging messages, agents X and Y execute a synchronous action."""


class IP11(IP5):
    """Concurrently with message exchange, agents X and Y execute a synchronous action."""


class IP12(IP6):
    """Agents X and Y either execute a synchronous action r exchange, but not both."""


############################################################################################################


# Step 3: Define Interface Pattern IP-1
def define_interface_pattern_ip1():
    """
    Defines the IP-1 interface pattern involving Agent A and Agent B.

    Returns:
        A tuple (net, initial_marking, final_marking) representing the IP-1 Petri net.
    """
    net = PetriNet("IP-1")

    # Define places
    p_a1 = PetriNet.Place("p_A1")
    p_b1 = PetriNet.Place("p_B1")
    p_a2 = PetriNet.Place("p_A2")

    net.places.add(p_a1)
    net.places.add(p_b1)
    net.places.add(p_a2)

    # Define transitions
    t_a1 = PetriNet.Transition("t_A1", "A1")
    t_b1 = PetriNet.Transition("t_B1", "B1")
    t_a2 = PetriNet.Transition("t_A2", "A2")

    net.transitions.add(t_a1)
    net.transitions.add(t_b1)
    net.transitions.add(t_a2)

    # Define arcs
    petri_utils.add_arc_from_to(p_a1, t_a1, net)
    petri_utils.add_arc_from_to(t_a1, p_b1, net)
    petri_utils.add_arc_from_to(p_b1, t_b1, net)
    petri_utils.add_arc_from_to(t_b1, p_a2, net)
    petri_utils.add_arc_from_to(p_a2, t_a2, net)

    # Initial and final markings
    initial_marking = Marking()
    final_marking = Marking()
    initial_marking[p_a1] = 1  # Start with A1
    final_marking[p_a2] = 1  # End after A2

    return net, initial_marking, final_marking
