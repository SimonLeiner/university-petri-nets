from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net.utils.petri_utils import add_place
from pm4py.objects.petri_net.utils.petri_utils import merge
from pm4py.objects.petri_net.utils.petri_utils import remove_transition


class MergeNets:
    """
    Merging two petri nets into one.

    Comments:
        - A rather Simple Implementation as it needs certain naming of the interacting transitions.
    """

    def __repr__(self) -> str:
        """String representation of the InterfacePattern object."""
        return f"<{self.__class__.__name__}>"

    @staticmethod
    def connect_async(net: PetriNet) -> None:
        """Connects Async transitions.

        Args:
            net (PetriNet): Petri Net.

        Comments:
            - It connects transitions with labels containing '!' (message sent) and connects
            them to corresponding transitions with labels containing '?' (message received).
            - It creates a new place for each pair of asynchronous transitions and connects the transitions to this new place.
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
    def connect_sync(net: PetriNet) -> None:
        """Connects Async transitions.

        Args:
            net (PetriNet): Petri Net.

        Comments:
            - Identifyies transitions with the same name and merging their incoming and outgoing arcs.
            - Removes duplicate transitions and marks the remaining transitions as "sync."
        """
        # shallow copy since we are modifiying the list
        transitions = net.transitions.copy()

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

    @staticmethod
    def merge(net1: PetriNet, net2: PetriNet) -> PetriNet:
        """
        Merging two petri nets into one.

        Args:
            net1 (PetriNet): First Petri Net.
            net2 (PetriNet): Second Petri Net.

        Returns:
            PetriNet: Merged Petri Net.
        """
        # merge the two nets
        merged_net = merge(nets=[net1, net2])

        # adjust the connections properly
        merged_net.connect_async(merged_net)
        merged_net.connect_sync(merged_net)

        return merged_net
