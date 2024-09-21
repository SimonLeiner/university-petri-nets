from collections import Counter

from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net.utils.petri_utils import add_place
from pm4py.objects.petri_net.utils.petri_utils import merge
from pm4py.objects.petri_net.utils.petri_utils import remove_transition


class MergeNets:
    """
    Merging two petri nets into one.

    Comments:
        - A rather Simple Implementation as it needs certain naming of the interacting transitions, like a! and a?.
    """

    def __repr__(self) -> str:
        """String representation of the InterfacePattern object."""
        return f"<{self.__class__.__name__}>"

    @staticmethod
    def encode_element(element: PetriNet.Place | PetriNet.Transition) -> str:
        """Make Sure recourse in properties is used if available, otherwise use default_string."""
        default_string = ""
        if "resource" in element.properties:
            default_string += element.properties["resource"]
        else:
            default_string += "undefined"
        default_string += ":"
        if isinstance(element, PetriNet.Place):
            default_string += element.name
        else:
            default_string += element.label if element.label != None else element.name
        return default_string

    @staticmethod
    def connect_async(net: PetriNet) -> PetriNet:
        """Connects Async transitions.

        Args:
            net (PetriNet): Petri Net.

        Comments:
            - It connects transitions with labels containing '!' (message sent) and connects
            them to corresponding transitions with labels containing '?' (message received).
            - It creates a new place for each pair of asynchronous transitions and connects the transitions to this new place.

        Returns:
            PetriNet: Petri Net.
        """
        # for every transition
        for trans in net.transitions:
            # check if trans is sending
            if trans.label and "!" in trans.label:
                # Find the receiving transition
                async_label = trans.label
                recv_label = async_label.replace("!", "?")

                # Update properties of the sending transition
                trans.properties.update({"resource": "!"})

                # Find the receiving transition
                recv_trans = next(
                    (t for t in net.transitions if t.label == recv_label),
                    None,
                )
                if recv_trans:
                    recv_trans.properties.update({"resource": "?"})

                    # Create a new place and add arcs
                    new_place = add_place(net, async_label)
                    new_place.properties.update({"resource": True})
                    add_arc_from_to(trans, new_place, net)
                    add_arc_from_to(new_place, recv_trans, net)

    @staticmethod
    def connect_sync(net: PetriNet) -> PetriNet:
        """Connects Sync transitions.

        Args:
            net (PetriNet): Petri Net.

        Comments:
            - Identifyies transitions with the same name and merging their incoming and outgoing arcs.
            - Removes duplicate transitions and marks the remaining transitions as "sync."

        Returns:
            PetriNet: Petri Net.
        """
        # TODO: shallow copy since we are modifiying the list
        transitions = net.transitions

        # for every transition
        for trans in transitions:
            # Find other transitions with the same name
            sync_transitions = [
                t for t in transitions if t.name == trans.name and t != trans
            ]
            for trans2 in sync_transitions:
                # Add missing arcs to the original transition
                for arc in trans2.in_arcs.copy():
                    add_arc_from_to(arc.source, trans, net)
                for arc in trans2.out_arcs.copy():
                    add_arc_from_to(trans, arc.target, net)
                # Mark transition as synchronous
                trans.properties["resource"] = "sync"
                # Remove the duplicate transition
                remove_transition(net, trans2)

        return net

    @staticmethod
    def add_markings(net: PetriNet) -> tuple[Marking, Marking]:
        """
        Define the initial and final markings of the Petri Net.

        Args:
            net (PetriNet): Petri Net.

        Returns:
            tuple[Marking, Marking]: Initial and Final Markings.
        """
        # initial marking is a place with no input arcs
        initial_marking = Marking()
        for place in net.places:
            if not place.in_arcs:
                initial_marking[place] = 1

        # final marking is a place with no output arcs
        final_marking = Marking()
        for place in net.places:
            if not place.out_arcs:
                final_marking[place] = 1

        return initial_marking, final_marking, net

    @staticmethod
    def merge_nets(net1: PetriNet, net2: PetriNet) -> tuple[Marking, Marking, PetriNet]:
        """
        Merging two petri nets into one.

        Args:
            net1 (PetriNet): First Petri Net.
            net2 (PetriNet): Second Petri Net.

        Returns:
            tuple[Marking, Marking, PetriNet]: Initial and Final Markings and the Merged Petri Net.
        """
        # merge the two nets
        merged_net = merge(nets=[net1, net2])

        # adjust the connections properly
        merged_net = MergeNets.connect_async(merged_net)
        merged_net = MergeNets.connect_sync(merged_net)

        # define the markings
        return MergeNets.add_markings(merged_net)

    @staticmethod
    def merge_markings(net1_marking: Marking, net2_marking: Marking) -> Marking:
        """
        Merging two Markings into one.


        Args:
            net1_marking (Marking): First Marking.
            net2_marking (Marking): Second Marking.

        Returns:
            Marking: Merged Marking.
        """
        return Marking(Counter(net1_marking) + Counter(net2_marking))


# Control the public API of the module
__all__ = ["MergeNets"]
