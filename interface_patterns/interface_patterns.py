"""This module contains the Interface Patterns."""

from abc import ABCMeta
from abc import abstractmethod


class InterfacePattern(metaclass=ABCMeta):
    """Base Class for Interface Patterns."""

    # TODO: Message in a dict or queue or Set? Exchange Messages via channels.

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
