import copy
import inspect
import logging
from collections import deque

import networkx as nx
import pandas as pd
from networkx.algorithms import isomorphism
from pm4py import read_xes
from pm4py import view_petri_net
from pm4py.objects.petri_net.obj import PetriNet
from tqdm import tqdm

from backend.compositional_algorithm.interface_patterns.interface_patterns import (
    BaseInterfacePattern,
)
from backend.compositional_algorithm.transformations.transformations import (
    BaseTransformation,
)
from backend.compositional_algorithm.transformations.transformations import (
    PlaceTransformation,
)
from backend.compositional_algorithm.transformations.transformations import (
    TransitionTransformation,
)


def discover(
    input_log_path: str,
    algorithm: callable,
    **algorithm_kwargs,  # noqa: ANN003
) -> PetriNet:
    """Discover a GWF-net (process model) for the agent using  for instance the Inductive Miner.

    Args:
        input_log_path (str): The path to the event log.
        algorithm (callable): The process discovery algorithm to use.
        algorithm_kwargs: Additional arguments to pass to the algorithm.

    Comments:
        - See implmentation: inductive_miner.apply(log, variant=variant, parameters=parameters)

    Returns:
        The discovered Petri net model for the agent.
    """
    # Inspect the algorithm's signature
    sig = inspect.signature(algorithm)
    parameters = list(sig.parameters.values())
    first_param = parameters[0]

    # Check if the first parameter is expected to be a string
    if isinstance(first_param.annotation, str):
        # If the algorithm expects a file path
        log_input = input_log_path
    else:
        # Convert the input log path to a DataFrame
        log_input = read_xes(input_log_path)

    net, initial_marking, final_marking = algorithm(log_input, **algorithm_kwargs)
    return net, initial_marking, final_marking


def check_net_valid(current_net: PetriNet, end_net: PetriNet) -> bool:
    """Checks if the net is valid.

    Args:
        current_net (PetriNet): The current net.
        end_net (PetriNet): The target net.

    Comment:
        - Time complexity: O(1)

    Returns:
        bool: True if the net is valid
    """
    # only one must be true to violate the condition
    return (
        len(current_net.places) <= len(end_net.places)
        and len(current_net.transitions) <= len(end_net.transitions)
        and len(current_net.arcs) <= len(end_net.arcs)
    )


def convert_petri_net_to_networkx(petri_net: PetriNet) -> nx.DiGraph:
    """Converts a Petri net from pm4py format to a networkx DiGraph.

    Args:
        petri_net (PetriNet): The Petri net to convert.

    Comments:
        - https://networkx.org/documentation/stable/reference/classes/digraph.html
        - The Petri net is a directed graph, so we use networkx's DiGraph.
        - Runtime of O(n) where n is the number of nodes.

    Returns:
        nx.DiGraph: The converted Petri net as a networkx
    """
    graph = nx.DiGraph()

    # Add places and transitions as nodes
    for place in petri_net.places:
        graph.add_node(place, type="place")

    for transition in petri_net.transitions:
        graph.add_node(transition, type="transition")

    # Add arcs as edges
    for arc in petri_net.arcs:
        graph.add_edge(arc.source, arc.target)

    return graph


def is_isomorphic(net1: PetriNet, net2: PetriNet) -> bool:
    """Checks if two Petri nets are identical.

    Args:
        net1 (PetriNet): The first Petri net.
        net2 (PetriNet): The second Petri net.

    Comments:
        - https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.isomorphism.is_isomorphic.html
        - The method works for generic graphs, and Petri nets can be represented as directed graphs.
        - uses the VF2 algorithm for graph isomorphism with O(n!) complexity.

    Returns:
        bool: True if the two Petri nets are isomorphic.
    """
    # Convert pm4py Petri nets to networkx graphs
    netx_petri_net1 = convert_petri_net_to_networkx(net1)
    netx_petri_net2 = convert_petri_net_to_networkx(net2)

    # Use networkx's is_isomorphic function
    return isomorphism.DiGraphMatcher(netx_petri_net1, netx_petri_net2).is_isomorphic()


def is_refinement(
    begin_net: PetriNet,
    end_net: PetriNet,
    transformations: list[BaseTransformation],
) -> tuple[bool, list[BaseTransformation]]:
    """Checks if the agent GWF-net is a proper refinement of the corresponding part in the interface pattern.

    Args:
        begin_net (PetriNet): The corresponding part in the interface pattern.
        end_net (PetriNet): The agent GWF-net.
        transformations (list): The list of transformations to apply.

    Comments:
        - We use BFS to find a sequence of transformations that transforms the input net into the target net.
        - TODO: We copy the nets so we apply one one sequence at a time. Is it legit to apply them also in parallel? -> Speed up?

    Returns:
        bool: True if the agent GWF-net is a refinement of the corresponding part in the interface pattern.
        list: The sequence of transformations that lead to the target
    """
    # split in place and transition transformations
    place_transformations = [
        t for t in transformations if isinstance(t(), PlaceTransformation)
    ]
    transition_transformations = [
        t for t in transformations if isinstance(t(), TransitionTransformation)
    ]

    # create a deep copy of the begin_net
    first_net = begin_net.__deepcopy__()

    # accidentially the same
    if is_isomorphic(first_net, end_net):
        logging.info("The nets are initially isomorphic.")
        return True, []

    # Create a queue for BFS and add the initial net
    queue = deque([(first_net, [])])

    # Initialize the set of visited states
    visited = set()
    visited.add(id(first_net))

    # as long as there is an element in the queue
    with tqdm(total=None, desc="Processing Queue") as pbar:
        while queue:
            # Update progress bar
            pbar.update(1)

            # dequeue the first element in the queue
            current_net, transformation_sequence = queue.popleft()
            view_petri_net(current_net)

            # Note: branching logic: we need to apply all possible transformations
            # for each place in the current net
            for place in current_net.places:
                # apply each possible place transformation
                for place_transformation in place_transformations:
                    # TODO: Necessary? ensures that subsequent transformations are applied to a fresh instance of the net.
                    # new_net = copy.deepcopy(current_net)
                    # new_net = current_net.__deepcopy__()
                    transformed_net = place_transformation.refine(place, current_net)
                    view_petri_net(transformed_net)

                    # check if the new net is the one we are looking for
                    if check_net_valid(transformed_net, end_net):
                        if is_isomorphic(transformed_net, end_net):
                            logging.info("The nets are isomorphic.")
                            return True, transformation_sequence
                        # if not, add the new net to the queue and save what transformation was applied
                        queue.append(
                            (
                                transformed_net,
                                [*transformation_sequence, place_transformation],
                            ),
                        )
                        # add the new net to the visited set
                        visited.add(id(transformed_net))

            # # for each transition in the current net
            # for transition in current_net.transitions:
            #     # apply each possible transition transformation
            #     for transition_transformation in transition_transformations:
            #         # Note: ensures that subsequent transformations are applied to a fresh instance of the net.
            #         new_net = copy.deepcopy(current_net)
            #         transformed_net = transition_transformation.refine(
            #             transition,
            #             new_net,
            #         )

            #         # check if the new net is the one we are looking for
            #         if check_net_valid(transformed_net, end_net):
            #             if is_isomorphic(transformed_net, end_net):
            #                 return True
            #             # if not, add the new net to the queue and save what transformation was applied
            #             queue.append(
            #                 (
            #                     transformed_net,
            #                     [*transformation_sequence, transition_transformation],
            #                 ),
            #             )
            #         # add the new net to the visited set
            #         visited.add(id(transformed_net))

    # If no sequence of transformations leads to the target net
    logging.info("No sequence of transformations leads to the target net.")
    return False, []


def replace(
    multi_agent_net: PetriNet,
    interface_subset_pattern: PetriNet,
    gwf_agent_net: PetriNet,
) -> PetriNet:
    """Substitutes the corresponding part in the interface pattern with the agent model.

    Args:
        multi_agent_net (PetriNet): The multi-agent system GWF-net.
        interface_subset_pattern (PetriNet): The corresponding part in the interface pattern.
        gwf_agent_net (PetriNet): The agent GWF-net.

    Returns:
        PetriNet: The updated multi-agent system GWF-net.
    """
    raise NotImplementedError


def compositional_discovery(
    df_log: pd.DataFrame,
    algorithm: callable,
    interface_pattern: BaseInterfacePattern,
    transformations: list[BaseTransformation],
    agent_column: str = "org:resource",
    **algorithm_kwargs: dict,
) -> PetriNet:
    """Compositional Process Discovery Algorithm as described in Algorithm 1.

    Args:
        df_log (pd.DataFrame): The event log for the multi-agent system.
        algorithm (callable): The process discovery algorithm to use.
        interface_pattern (BaseInterfacePattern): The interface pattern to use that consists of A1,...An Agents.
        transformations (list[BaseTransformation]): The list of transformations
        agent_column (str): The column in the event log that contains the agent names.
        algorithm_kwargs (dict): Additional arguments to pass to the algorithm.

    Comments:
        - TODO: Checks agent i for subnet i and not agent i for all subnets.
        - Time Complexity: ...

    Returns:
        multi_agent_net (Petri net): a multi-agent system GWF-net.
    """
    # init multi agent system gwf net S
    multi_agent_net = interface_pattern

    # For each agent in the event log
    unique_agents = df_log[agent_column].unique()

    with tqdm(total=len(unique_agents), desc="Processing Agents") as pbar:
        # for each agent in the event log
        for i, agent in enumerate(unique_agents):
            # create sub-logs
            df_log_agent = df_log[df_log[agent_column] == agent]

            # discover net
            gwf_agent_net, _, _ = discover(df_log_agent, algorithm, **algorithm_kwargs)

            # get the corresponding interface subset pattern
            interface_subset_pattern = interface_pattern.get_net(f"A{i}")

            # check if discovered net is a refinement of the interface pattern for Agent Ai
            check_refinement, transformation_list = is_refinement(
                gwf_agent_net,
                interface_subset_pattern,
                transformations,
            )

            # log the result
            logging.info(
                f"Agent {agent} is a refinement: {check_refinement} with transformations: {transformation_list}",
            )

            if check_refinement:
                # substitute the agent model with the corresponding part in the interface pattern
                multi_agent_net = replace(
                    multi_agent_net,
                    interface_subset_pattern,
                    gwf_agent_net,
                )

            # Update progress bar
            pbar.update(1)

    return multi_agent_net
