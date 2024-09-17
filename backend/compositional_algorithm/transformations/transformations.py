from abc import ABCMeta
from abc import abstractmethod

from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net.utils.petri_utils import add_place
from pm4py.objects.petri_net.utils.petri_utils import add_transition
from pm4py.objects.petri_net.utils.petri_utils import get_transition_by_name


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

    @staticmethod
    def get_place_by_name(net: PetriNet, place_name: str) -> PetriNet.Place | None:
        """Get a transition by its name.

        Args:
            net (PetriNet): The Petri Net to search in.
            place_name (str): The name of the place to search for.

        Comments:
            - Inspired by get_transition_by_name from pm4py.objects.petri_net.utils.petri_utils

        Returns:
            - Place: The place with the given name.

        """
        for p in net.places:
            if p.name == place_name:
                return p
        return None


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
        # Note: if we create a copy of the net, the places are not the same anymore, just the names
        wanted_place = P1.get_place_by_name(net, place_name=place.name)

        # Note: can't use "place not in net.places:" since we work with a deep copy of the Petri net and the ids are different.
        if wanted_place is None:
            msg = f"Place {place.name} not found in Petri net."
            raise ValueError(msg)

        # Create a new place
        new_place = add_place(net, name=wanted_place.name)

        # Adjust incoming arcs
        for in_arc in wanted_place.in_arcs:
            add_arc_from_to(in_arc.source, new_place, net)

        # Adjust outgoing arcs
        for out_arc in wanted_place.out_arcs:
            add_arc_from_to(new_place, out_arc.target, net)

        # TODO: What about the marking? -> If p is part of the initial marking, both p1 and p2 must be marked in the new net.

        return net

    @staticmethod
    def abstract() -> PetriNet:
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
        # Note: if we create a copy of the net, the places are not the same anymore, just the names
        wanted_transition = get_transition_by_name(net, place_name=transition.name)

        # Note: can't use "place not in net.places:" since we work with a deep copy of the Petri net and the ids are different.
        if wanted_transition is None:
            msg = f"Transition {transition.name} not found in Petri net."
            raise ValueError(msg)

        # Create a new transition: t1 and t2 have the same label as t
        new_transition = add_transition(
            net,
            name=transition.name,
            label=transition.label,
        )

        # Adjust incoming arcs
        for in_arc in wanted_transition.in_arcs:
            add_arc_from_to(in_arc.source, new_transition, net)

        # Adjust outgoing arcs
        for out_arc in wanted_transition.out_arcs:
            add_arc_from_to(new_transition, out_arc.target, net)

        # What about the marking?

        return net

    @staticmethod
    def abstract() -> PetriNet:
        """Apply the inverse of Transition Duplication (merge two transitions into one).

        Args:
            transition1 (Transition): The first transition to merge.
            transition2 (Transition): The second transition to merge.
            net (PetriNet): The Petri Net to abstract.

        Returns:
            - PetriNet: The abstracted Petri Net.
        """
        msg = "P2 abstract method not implemented yet."
        raise NotImplementedError(msg)


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
        # Note: if we create a copy of the net, the places are not the same anymore, just the names
        wanted_place = P1.get_place_by_name(net, place_name=place.name)

        # Note: can't use "place not in net.places:" since we work with a deep copy of the Petri net and the ids are different.
        if wanted_place is None:
            msg = f"Place {place.name} not found in Petri net."
            raise ValueError(msg)

        # Create new places
        new_place = add_place(net, name=wanted_place.name)

        # Note: Create a new transition t. t is not labeled with an interacting action.
        new_transition = add_transition(net, label="t")

        # Add arcs: p1 to t, and t to p2
        add_arc_from_to(wanted_place, new_transition, net)
        add_arc_from_to(new_transition, new_place, net)

        for arc in wanted_place.out_arcs:
            add_arc_from_to(new_place, arc.target, net)

        # What about the marking?

        return net

    @staticmethod
    def abstract() -> PetriNet:
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
        # Note: if we create a copy of the net, the places are not the same anymore, just the names
        wanted_place = P1.get_place_by_name(net, place_name=place.name)

        # Note: can't use "place not in net.places:" since we work with a deep copy of the Petri net and the ids are different.
        if wanted_place is None:
            msg = f"Place {place.name} not found in Petri net."
            raise ValueError(msg)

        # Get all incoming arcs of the place
        incoming_arcs = list(wanted_place.in_arcs)

        # Check if there are enough incoming arcs to split. Otherwise, return the net as it is.
        if len(incoming_arcs) <= 1:
            return net

        # add new place
        new_place = add_place(net, wanted_place.name)

        # Systematically split the incoming arcs. For example, if there are 2 incoming arcs, split_index = 1
        split_index = len(incoming_arcs) // 2

        # create subsets p1 and p2.
        in_arcs_p1 = incoming_arcs[:split_index]
        in_arcs_p2 = incoming_arcs[split_index:]

        # subset arcs to old place
        for arc in in_arcs_p1:
            add_arc_from_to(arc.source, wanted_place, net)
            net.remove_arc(arc)

        # subset arcs to new place
        for arc in in_arcs_p2:
            add_arc_from_to(arc.source, new_place, net)

        # post set of p1, p2 are two complete copies of p -> Duplicate the outgoing arcs
        for arc in wanted_place.out_arcs:
            add_arc_from_to(new_place, arc.target, net)

        # What about the marking?

        return net

    @staticmethod
    def abstract() -> PetriNet:
        """Apply the inverse of Place Split (merge two places into one).

        Args:
            place1 (Place): The first place to merge.
            place2 (Place): The second place to merge.
            net (PetriNet): The Petri Net to abstract.

        Returns:
            - PetriNet: The abstracted Petri Net.
        """
        msg = "P4 abstract method not implemented yet."
        raise NotImplementedError(msg)


# List of supported transformations
TRANSFORMATIONS: list[BaseTransformation] = [
    P1,
    P2,
    P3,
    P4,
]

# Control the public API of the module
__all__ = ["TRANSFORMATIONS"]
