import difflib
from collections import Counter

from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net.utils.petri_utils import add_place
from pm4py.objects.petri_net.utils.petri_utils import add_transition
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
    def connect_async(net: PetriNet) -> None:
        """Connects Async transitions.

        Args:
            net (PetriNet): Petri Net.

        Comments:
            - "Inplace"
            - It connects transitions with labels containing '!' (message sent) and connects
            them to corresponding transitions with labels containing '?' (message received).
            - It creates a new place for each pair of asynchronous transitions and connects the transitions to this new place.

        """
        for send_trans in net.transitions:
            # check if trans is sending
            if send_trans.label and "!" in send_trans.label:
                # Find the receiving transition
                async_label = send_trans.label
                recv_label = async_label.replace("!", "?")

                # recieving transitions
                recieving_transitions1 = [
                    t for t in net.transitions if t.label and recv_label in t.label
                ]
                recieving_transitions2 = [
                    t for t in net.transitions if t.label and t.label in recv_label
                ]
                # combine lists and make unique
                recieving_transitions = list(
                    set(recieving_transitions1 + recieving_transitions2),
                )

                if len(recv_label) > 5:  # noqa: PLR2004
                    for t in net.transitions:
                        if t.label:  # noqa: SIM102
                            if (
                                recv_label
                                and "?" in t.label
                                and t.label not in recieving_transitions
                                and t.label != recv_label
                            ):
                                differences = sum(
                                    1
                                    for a, b in zip(t.label, recv_label, strict=False)
                                    if a != b
                                )

                                # very similar, but not subsets like: "Activity C_m2?" and "Activity CZ_m2?"
                                threshold = 0.7
                                if differences <= 4:  # noqa: PLR2004
                                    similarity = difflib.SequenceMatcher(
                                        None,
                                        t.label,
                                        recv_label,
                                    ).ratio()
                                    if similarity >= threshold:
                                        recieving_transitions.append(t)

                for recv_trans in recieving_transitions:
                    if recv_trans:
                        # Create a new place and add arcs
                        new_place = add_place(net, f"p_{async_label}")
                        add_arc_from_to(send_trans, new_place, net)
                        add_arc_from_to(new_place, recv_trans, net)

    @staticmethod
    def connect_sync(net: PetriNet) -> None:
        """Connects Sync transitions.

        Args:
            net (PetriNet): Petri Net.

        Comments:
            - "Inplace"
            - Identifyies transitions with the same name and merging their incoming and outgoing arcs.
            - Removes duplicate transitions and marks the remaining transitions as "sync."

        """
        # Shallow copy since we need the transitions from the original net and we modify
        transitions1 = net.transitions.copy()

        # Set to keep track of processed transitions
        processed_transitions = set()

        # For every transition
        for trans in transitions1:
            # Skip if already processed
            if trans in processed_transitions:
                continue

            # Find other transitions with the same label
            sync_transitions = []
            for t in net.transitions:
                if t.label and (t.label == trans.label and t != trans):
                    sync_transitions.append(t)  # noqa: PERF401

            # If there are other transitions with the same label
            for trans2 in sync_transitions:
                # Merge arcs into the original transition (trans)
                for arc in trans2.in_arcs.copy():
                    add_arc_from_to(arc.source, trans, net)
                for arc in trans2.out_arcs.copy():
                    add_arc_from_to(trans, arc.target, net)

                # Remove the duplicate transition (trans2) but keep the original (trans) intact
                remove_transition(net, trans2)

                # Mark trans2 as processed
                processed_transitions.add(trans2)

            # Mark trans as processed
            processed_transitions.add(trans)

    @staticmethod
    def merge_nets(nets: list[PetriNet]) -> PetriNet:
        """
        Merging two petri nets into one.

        Args:
            nets (list[PetriNet]): List

        Returns:
            PetriNet: Merged Petri Net.
        """
        # merge the two nets
        merged_net = merge(nets=nets)

        # adjust the connections properly
        MergeNets.connect_async(merged_net)
        MergeNets.connect_sync(merged_net)

        return merged_net

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
            if len(place.in_arcs) == 0:
                initial_marking[place] = 1

        # final marking is a place with no output arcs
        final_marking = Marking()
        for place in net.places:
            if len(place.out_arcs) == 0:
                final_marking[place] = 1

        return initial_marking, final_marking

    @staticmethod
    def conformance_adapter(net: PetriNet) -> PetriNet:
        """Adjust the net for conformance calculation.

        Args:
            net (PetriNet): Petri Net.


        Comments:
            - Since Precision/Fitness and Entropy need a single start and end place, this function is used to adjust the net.
            - Intrudoce a place and transition to the net to have a single start and end place.

        Returns:
            PetriNet: Adjusted Petri Net.
        """
        # want new net
        conf_net = net.__deepcopy__()

        # add a new start place
        start_place = add_place(conf_net, "Start")
        # add a new transition
        start_transition = add_transition(
            conf_net,
            name="Start",
            label="Start",
        )

        # add a new end place
        end_place = add_place(conf_net, "End")
        # add a new transition
        end_transition = add_transition(
            conf_net,
            name="End",
            label="End",
        )

        # add arcs
        add_arc_from_to(end_transition, end_place, conf_net)
        add_arc_from_to(start_place, start_transition, conf_net)
        for place in conf_net.places:
            # begin
            if len(place.in_arcs) == 0 and place != start_place:
                add_arc_from_to(start_transition, place, conf_net)
            # end
            if len(place.out_arcs) == 0 and place != end_place:
                add_arc_from_to(place, end_transition, conf_net)

        # add marking
        initial_marking, final_marking = MergeNets.add_markings(conf_net)
        return conf_net, initial_marking, final_marking


# Control the public API of the module
__all__ = ["MergeNets"]
