from abc import ABCMeta
from abc import abstractmethod

from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net.utils.petri_utils import add_place
from pm4py.objects.petri_net.utils.petri_utils import add_transition


"""# Make a deep copy of the original net
multiple_refined_net = ip1_net_a1.__deepcopy__()

# Apply each transformation sequentially
for transformation in place_transformations:
    new_multiple_refined_net = multiple_refined_net.__deepcopy__()
    for place in multiple_refined_net.places:
        new_multiple_refined_net = transformation.refine(
            place,
            new_multiple_refined_net,
        )
    # Update multiple_refined_net to the latest transformed net
    multiple_refined_net = new_multiple_refined_net

# Apply each transformation sequentially
for transformation in transition_transformations:
    new_multiple_refined_net = multiple_refined_net.__deepcopy__()
    for transition in multiple_refined_net.transitions:
        new_multiple_refined_net = transformation.refine(
            transition,
            new_multiple_refined_net,
        )
    # Update multiple_refined_net to the latest transformed net
    multiple_refined_net = new_multiple_refined_net

pm4py.view_petri_net(multiple_refined_net, initial_marking, final_marking, format="png")"""


class BaseTransformation(metaclass=ABCMeta):
    """Abstract base class for Transformations."""

    @abstractmethod
    def refine(self) -> None:
        """Refine transformations."""

    @abstractmethod
    def abstract(self) -> None:
        """Abstract transformations."""

    def __repr__(self) -> str:
        """String representation of the InterfacePattern object."""
        return f"<{self.__class__.__name__}>"


class PlaceTransformation(BaseTransformation):
    pass


class TransitionTransformation(BaseTransformation):
    """Transition Naming: For example a! -> a1! and a2! is not allowed."""


class P1(PlaceTransformation):
    """
    P1 Transformation (Place Duplication).

    In this transformation, the place p is duplicated into two places (p1, p2), keeping the same input/output transitions (t1, t2).

    Constraints:
        - The input transitions to p1 and p2 are the same as p (before duplication).
        - The output transitions from p1 and p2 are the same as p.
        - If p is part of the initial marking, both p1 and p2 must be marked in the new net.
    """

    @staticmethod
    def refine(place: PetriNet.Place, net: PetriNet) -> PetriNet:
        """Apply a Place duplication.

        Args:
            place (Place): The place to duplicate (Given by name).
            net (PetriNet): The Petri Net to refine.

        Returns:
            - PetriNet: The refined Petri Net.
        """
        # TODO: Check if the place to duplicate exists in the Petri net
        # if place.name not in [p.name for p in net.places]:
        #     msg = f"Place {place.name} not found in Petri net."
        #     raise ValueError(msg)
        if place not in net.places:
            msg = f"Place {place.name} not found in Petri net."
            raise ValueError(msg)

        # Create a new place
        new_place = add_place(net, name=place.name)

        # Adjust incoming arcs
        for in_arc in place.in_arcs:
            add_arc_from_to(in_arc.source, new_place, net)

        # Adjust outgoing arcs
        for out_arc in place.out_arcs:
            add_arc_from_to(new_place, out_arc.target, net)

        # What about the marking?

        return net

    @staticmethod
    def abstract(
        net: PetriNet,
        place1: PetriNet.Place,
        place2: PetriNet.Place,
    ) -> PetriNet:
        """Apply the inverse of Place Duplication (merge two places into one).

        Args:
            net (PetriNet): The Petri Net to abstract.
            place1 (Place): The first place to merge.
            place2 (Place): The second place to merge.

        Returns:
            - PetriNet: The abstracted Petri Net.
        """
        msg = "P1 abstract method not implemented yet."
        raise NotImplementedError(msg)
        # Check if both places to merge exist
        if place1 not in net.places or place2 not in net.places:
            msg = f"One or both places {place1} and {place2} not found in Petri net."
            raise ValueError(msg)

        # Create a new place representing the original place before duplication
        merged_place = add_place(net, "p")

        # Merge incoming arcs: connect all input transitions from both places to the new place
        for in_arc in set(place1.in_arcs) | set(place2.in_arcs):
            if in_arc.source not in [arc.source for arc in merged_place.in_arcs]:
                add_arc_from_to(in_arc.source, merged_place, net)
                net.arcs.remove(in_arc)

        # Merge outgoing arcs: connect all output transitions from both places to the new place
        for out_arc in set(place1.out_arcs) | set(place2.out_arcs):
            if out_arc.target not in [arc.target for arc in merged_place.out_arcs]:
                add_arc_from_to(merged_place, out_arc.target, net)
                net.arcs.remove(out_arc)

        # Remove the old places from the net
        net.places.remove(place1)
        net.places.remove(place2)

        # What about the marking?

        return net


class P2(TransitionTransformation):
    """P2 Transformation (Transition Duplication)."""

    @staticmethod
    def refine(transition: PetriNet.Transition, net: PetriNet) -> PetriNet:
        """Apply a Transition duplication.

        Args:
            transition (Transition): The transition to duplicate (Given by name).
            net (PetriNet): The Petri Net to refine.

        Returns:
            - PetriNet: The refined Petri Net.
        """
        # retrieve the transition to duplicate
        if transition not in net.transitions:
            msg = f"Transition {transition} not found in Petri net."
            raise ValueError(msg)

        # Create new transitions
        new_transition1 = add_transition(net, name=f"{transition.name}_1")
        new_transition2 = add_transition(net, name=f"{transition.name}_2")

        # Duplicate incoming arcs from the original transition to both new transitions and remove the original arcs
        for in_arc in list(transition.in_arcs):
            add_arc_from_to(in_arc.source, new_transition1, net)
            add_arc_from_to(in_arc.source, new_transition2, net)
            net.arcs.remove(in_arc)

        # Duplicate outgoing arcs from the original transition to both new transitions and remove the original arcs
        for out_arc in list(transition.out_arcs):
            add_arc_from_to(new_transition1, out_arc.target, net)
            add_arc_from_to(new_transition2, out_arc.target, net)
            net.arcs.remove(out_arc)

        # Remove the old transition from the net
        net.transitions.remove(transition)

        # What about the marking?

        return net

    @staticmethod
    def abstract(
        transition1: PetriNet.Transition,
        transition2: PetriNet.Transition,
        net: PetriNet,
    ) -> PetriNet:
        """Apply the inverse of Transition Duplication (merge two transitions into one).

        Args:
            transition1 (Transition): The first transition to merge.
            transition2 (Transition): The second transition to merge.
            net (PetriNet): The Petri Net to abstract.

        Returns:
            - PetriNet: The abstracted Petri Net.
        """
        # Check if both transitions to merge exist
        if transition1 not in net.transitions or transition2 not in net.transitions:
            msg = f"One or both transitions {transition1} and {transition2} not found in Petri net."
            raise ValueError(msg)

        # Create a new transition representing the original transition before duplication
        merged_transition = add_transition(net, "t")

        # Merge incoming arcs: connect all input places from both transitions to the new transition
        for in_arc in set(transition1.in_arcs) | set(transition2.in_arcs):
            if in_arc.source not in [arc.source for arc in merged_transition.in_arcs]:
                add_arc_from_to(in_arc.source, merged_transition, net)
                net.arcs.remove(in_arc)

        # Merge outgoing arcs: connect all output places from both transitions to the new transition
        for out_arc in set(transition1.out_arcs) | set(transition2.out_arcs):
            if out_arc.target not in [arc.target for arc in merged_transition.out_arcs]:
                add_arc_from_to(merged_transition, out_arc.target, net)
                net.arcs.remove(out_arc)

        # Remove the old transitions from the net
        net.transitions.remove(transition1)
        net.transitions.remove(transition2)

        # What about the marking?

        return net


class P3(PlaceTransformation):
    """P3 Transformation (Local transition introduction)."""

    @staticmethod
    def refine(
        place: PetriNet.Place,
        net: PetriNet,
    ) -> PetriNet:
        """Apply a Local transition introduction.

        Args:
            place (Place): The place to refine.
            transition (Transition): The transition to introduce.
            net (PetriNet): The Petri Net to refine.

        Returns:
            - PetriNet: The refined Petri Net.
        """
        # TODO: Check if the place to duplicate exists in the Petri net
        if place.name not in [p.name for p in net.places]:
            msg = f"Place {place.name} not found in Petri net."
            raise ValueError(msg)
        if place not in net.places:
            msg = f"Place {place.name} not found in Petri net."
            raise ValueError(msg)

        # Create new places
        new_place1 = add_place(net, name=f"{place.name}_1")
        new_place2 = add_place(net, name=f"{place.name}_2")

        # Create a new transition t
        new_transition = add_transition(net, "t")

        # Add arcs: p1 to t, and t to p2
        add_arc_from_to(new_place1, new_transition, net)
        add_arc_from_to(new_transition, new_place2, net)

        # # Duplicate incoming arcs from the original place to place 1 and remove the original arcs
        for arc in place.in_arcs:
            add_arc_from_to(arc.source, new_place1, net)
            net.arcs.remove(arc)

        for arc in place.out_arcs:
            add_arc_from_to(new_place2, arc.target, net)
            net.arcs.remove(arc)

        # Remove the old place from the net
        net.places.remove(place)

        # What about the marking?

        return net

    @staticmethod
    def abstract(
        place1: PetriNet.Place,
        place2: PetriNet.Place,
        transition: PetriNet.Transition,
        net: PetriNet,
    ) -> PetriNet:
        """Apply the inverse of Local transition introduction (remove a local transition).

        Args:
            place1 (Place): The first place to merge.
            place2 (Place): The second place to merge.
            transition (Transition): The transition to remove.
            net (PetriNet): The Petri Net to abstract.

        Returns:
            - PetriNet: The abstracted Petri Net.
        """
        msg = "P3 abstract method not implemented yet."
        raise NotImplementedError(msg)
        # Check if the transition and places exist in the Petri net
        if transition not in net.transitions:
            msg = "Transition does not exist in the Petri net."
            raise ValueError(msg)
        if place1 not in net.places or place2 not in net.places:
            msg = "One or both places do not exist in the Petri net."
            raise ValueError(msg)

        # Create a new place to replace p1 and p2
        new_place = add_place(net, "p")

        # Duplicate incoming arcs: from place1 to the new place
        for in_arc in place1.in_arcs:
            add_arc_from_to(in_arc.source, new_place, net)
            net.arcs.remove(in_arc)

        # Duplicate outgoing arcs: from the new place to place2
        for out_arc in place2.out_arcs:
            add_arc_from_to(new_place, out_arc.target, net)
            net.arcs.remove(out_arc)

        # Remove the old places and transition
        net.places.remove(place1)
        net.places.remove(place2)
        net.transitions.remove(transition)

        # What about the marking?

        return net


class P4(PlaceTransformation):
    """P4 Transformation (Place split)."""

    @staticmethod
    def refine(
        place: PetriNet.Place,
        net: PetriNet,
    ) -> PetriNet:
        """Apply a Place split.

        Args:
            place (Place): The place to split.
            net (PetriNet): The Petri Net to refine.

        Returns:
            - PetriNet: The refined Petri Net.
        """
        # Check if the place to split exists
        if place not in net.places:
            msg = f"Place {place} not found in Petri net."
            raise ValueError(msg)

        # Get all incoming arcs of the place
        incoming_arcs = list(place.in_arcs)

        # Check if there are enough incoming arcs to split
        if len(incoming_arcs) <= 1:
            msg = "The place does not have enough incoming arcs to perform a split."
            raise ValueError(
                msg,
            )

        # Create new places
        new_place1 = add_place(net, name=f"{place.name}_1")
        new_place2 = add_place(net, name=f"{place.name}_2")

        # Duplicate the incoming arcs
        # Systematically split the incoming arcs
        # Add incoming arcs to p1 and p2
        split_index = len(incoming_arcs) // 2
        in_arcs_p1 = incoming_arcs[:split_index]
        in_arcs_p2 = incoming_arcs[split_index:]
        for arc in in_arcs_p1:
            add_arc_from_to(arc.source, new_place1, net)
            net.arcs.remove(arc)
        for arc in in_arcs_p2:
            add_arc_from_to(arc.source, new_place2, net)
            net.remove_arc(arc)

        # Duplicate the outgoing arcs
        for arc in list(place.out_arcs):
            add_arc_from_to(new_place1, arc.target, net)
            add_arc_from_to(new_place2, arc.target, net)
            net.arcs.remove(arc)

        # Remove the old place
        net.places.remove(place)

        # What about the marking?

        return net

    @staticmethod
    def abstract(
        place1: PetriNet.Place,
        place2: PetriNet.Place,
        net: PetriNet,
    ) -> PetriNet:
        """Apply the inverse of Place Split (merge two places into one).

        Args:
            place1 (Place): The first place to merge.
            place2 (Place): The second place to merge.
            net (PetriNet): The Petri Net to abstract.

        Returns:
            - PetriNet: The abstracted Petri Net.
        """
        # Check if both places to merge exist
        if place1 not in net.places or place2 not in net.places:
            msg = f"One or both places {place1} and {place2} not found in Petri net."
            raise ValueError(msg)

        # Create a new place representing the original place before splitting
        merged_place = add_place(net, "p")

        # Merge incoming arcs: connect all input transitions from both places to the new place
        for in_arc in set(place1.in_arcs) | set(place2.in_arcs):
            if in_arc.source not in [arc.source for arc in merged_place.in_arcs]:
                add_arc_from_to(in_arc.source, merged_place, net)
                net.arcs.remove(in_arc)

        # Merge outgoing arcs: connect all output transitions from both places to the new place
        for out_arc in set(place1.out_arcs) | set(place2.out_arcs):
            if out_arc.target not in [arc.target for arc in merged_place.out_arcs]:
                add_arc_from_to(merged_place, out_arc.target, net)
                net.arcs.remove(out_arc)

        # Remove the old places from the net
        net.places.remove(place1)
        net.places.remove(place2)

        # What about the marking?

        return net


# List of supported transformations
TRANSFORMATIONS: list[BaseTransformation] = [
    P1,
    P2,
    P3,
    P4,
]

# Control the public API of the module
__all__ = ["TRANSFORMATIONS"]
