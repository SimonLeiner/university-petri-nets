from abc import ABCMeta
from abc import abstractmethod

from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net.utils.petri_utils import add_place


def refine_p1() -> PetriNet:
    """P1 Transformation (Place Duplication)."""
    raise NotImplementedError


def abstract_p1() -> PetriNet:
    """P1 Inverse Transformation (Place Merging)."""
    raise NotImplementedError


# TODO: Depreciated. Will be removed in the future.


class BaseTransformation(metaclass=ABCMeta):
    """Abstract base class for Transformations."""

    def __repr__(self) -> str:
        """String representation of the Transformations object."""
        return f"<{self.__class__.__name__}>"

    def __init__(
        self,
        net: PetriNet,
        initial_marking: Marking,
        final_marking: Marking,
    ) -> None:
        """
        Initializes the Petri net and markings.

        Args:
            net (PetriNet): The Petri net.
            initial_marking (Marking): The initial marking.
            final_marking (Marking): The final marking.
        """
        self.net = net
        self.initial_marking = initial_marking
        self.final_marking = final_marking

    @abstractmethod
    def apply_refinement(self) -> None:
        """Define the places."""

    @abstractmethod
    def apply_abstraction(self) -> None:
        """Abstract the places."""


class P1(BaseTransformation):
    """
    P1 Transformation (Place Duplication).

    In this transformation, the place p is duplicated into two places (p1, p2), keeping the same input/output transitions (t1, t2).

    Constraints:
        - The input transitions to p1 and p2 are the same as p (before duplication).
        - The output transitions from p1 and p2 are the same as p.
        - If p is part of the initial marking, both p1 and p2 must be marked in the new net.
    """

    def apply_refinement(self, place: PetriNet.Place) -> None:
        """Apply a Place duplication.

        Args:
            place (Place): The place to duplicate.
        """
        # Create two new places
        new_place1 = add_place(self.net)
        new_place2 = add_place(self.net)

        # Move incoming arcs from the original place to both new places and remove the original arcs
        for in_arc in list(place.in_arcs):
            add_arc_from_to(in_arc.source, new_place1, self.net)
            add_arc_from_to(in_arc.source, new_place2)
            self.net.arcs.remove(in_arc)

        # Move outgoing arcs from the original place to both new places and remove the original arcs
        for out_arc in list(place.out_arcs):
            add_arc_from_to(new_place1, out_arc.target, self.net)
            add_arc_from_to(new_place2, out_arc.target, self.net)
            self.net.arcs.remove(out_arc)

        # If the original place is marked in the initial marking, mark both new places and remove the marking from the original place
        if place in self.initial_marking:
            self.initial_marking[new_place1] = self.initial_marking[place]
            self.initial_marking[new_place2] = self.initial_marking[place]
            del self.initial_marking[place]

        # Remove the old place from the net
        self.net.places.remove(place)

    def apply_abstraction(self, place1: PetriNet.Place, place2: PetriNet.Place) -> None:
        """Apply the inverse of Place Duplication (merge two places into one).

        Args:
            place1 (Place): The first place to merge.
            place2 (Place): The second place to merge.
        """
        # Create a new place representing the original place before duplication
        merged_place = add_place(self.net)

        # Merge incoming arcs: connect all input transitions from both places to the new place
        for in_arc in list(place1.in_arcs) + list(place2.in_arcs):
            if in_arc.source not in [arc.source for arc in merged_place.in_arcs]:
                add_arc_from_to(in_arc.source, merged_place, self.net)

        # Merge outgoing arcs: connect all output transitions from both places to the new place
        for out_arc in list(place1.out_arcs) + list(place2.out_arcs):
            if out_arc.target not in [arc.target for arc in merged_place.out_arcs]:
                add_arc_from_to(merged_place, out_arc.target, self.net)

        # If either of the original places was marked in the initial marking, mark the merged place
        if place1 in self.initial_marking or place2 in self.initial_marking:
            marking_value = max(
                self.initial_marking.get(place1, 0),
                self.initial_marking.get(place2, 0),
            )
            self.initial_marking[merged_place] = marking_value
            if place1 in self.initial_marking:
                del self.initial_marking[place1]
            if place2 in self.initial_marking:
                del self.initial_marking[place2]

        # Remove the old places from the net
        self.net.places.remove(place1)
        self.net.places.remove(place2)


class P2(BaseTransformation):
    """P2 Transformation (Transition Duplication)."""


class P3(BaseTransformation):
    """P3 Transformation (Local transition introduction)."""


class P4(BaseTransformation):
    """P4 Transformation (Place split)."""
