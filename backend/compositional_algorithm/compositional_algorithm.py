import hashlib
import inspect
import json
import logging
from collections import deque
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism
from pm4py import read_xes
from pm4py import view_petri_net
from pm4py import write_xes
from pm4py.objects.petri_net.obj import PetriNet
from tqdm import tqdm

from backend.compositional_algorithm.combine_nets.combine_nets import MergeNets
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


# Configure the logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
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

    # Note: check based on what the discover algorithm expects
    # Split miner needs input path
    if isinstance(first_param.annotation, str):
        # keep it as it is
        log_input = input_log_path
    else:
        # Convert the input log path to a DataFrame
        log_input = read_xes(input_log_path)

    net, initial_marking, final_marking = algorithm(log_input, **algorithm_kwargs)
    return net, initial_marking, final_marking


def is_valid(
    current_net: PetriNet,
    end_net: PetriNet,
) -> bool:
    """Checks if the net is valid.

    Args:
        current_net (PetriNet): The current net.
        end_net (PetriNet): The target net.

    Comment:
        - Time complexity: O(n)

    Returns:
        bool: True if the net is valid
    """
    # only a certain number of places, transitions and arcs
    valid = (
        len(current_net.places) <= len(end_net.places)
        and len(current_net.transitions) <= len(end_net.transitions)
        and len(current_net.arcs) <= len(end_net.arcs)
    )

    # Identify source places (no incoming arcs) and sink places (no outgoing arcs)
    curr_net_source_places = [
        place
        for place in current_net.places
        if not any(arc.target == place for arc in current_net.arcs)
    ]
    end_net_source_places = [
        place
        for place in end_net.places
        if not any(arc.target == place for arc in end_net.arcs)
    ]
    curr_net_sink_places = [
        place
        for place in current_net.places
        if not any(arc.source == place for arc in current_net.arcs)
    ]
    end_net_sink_places = [
        place
        for place in end_net.places
        if not any(arc.source == place for arc in end_net.arcs)
    ]
    valid = (
        valid
        and len(curr_net_source_places) <= len(end_net_source_places)
        and len(curr_net_sink_places) <= len(end_net_sink_places)
    )

    # it is highly unlikely to apply a place or transformation split 10 times in a row, wo we prune them from the tree as well
    max_same = 5
    place_names = [place.name for place in current_net.places]
    transition_names = [transition.name for transition in current_net.transitions]
    all_names = place_names + transition_names
    name_count = {name: all_names.count(name) for name in set(all_names)}
    for count in name_count.values():
        if count > max_same:
            valid = False

    return valid


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


def is_refinement(  # noqa: C901
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
        - We copy the nets so we apply one one sequence at a time.
        - It is not legit to apply multiple transformations at the same time -> Nets immediately explode without search.
        - Time complexity: O()

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
    final_end_net = end_net.__deepcopy__()

    # accidentially the same
    if is_isomorphic(first_net, final_end_net):
        logging.info("The nets are initially isomorphic.")
        return True, []

    # Create a queue for BFS and add the initial net
    queue = deque([(first_net, [])])

    # Initialize the set of visited states
    visited = set()
    visited.add(generate_unique_id(first_net))

    # as long as there is an element in the queue
    with tqdm(total=None, desc="Processing Queue") as pbar:
        while queue:
            # Update progress bar
            pbar.update(1)

            # dequeue the first element in the queue
            current_net, transformation_sequence = queue.popleft()

            """# plotting of discovered net
            logging.info("Discovering new net.")
            view_petri_net(current_net, format="png")"""

            # Note: branching logic: we need to apply all possible transformations
            # for each place in the current net
            for place in current_net.places:
                # apply each possible place transformation
                for place_transformation in place_transformations:
                    # Note: Deep copy of the current net before applying the transformation -> transformation change places & transitions and sets are immutable.
                    net_copy = current_net.__deepcopy__()
                    transformed_net = place_transformation.refine(place, net_copy)
                    unique_net_id = generate_unique_id(transformed_net)

                    # check if the new net is the one we are looking for
                    if unique_net_id not in visited and is_valid(
                        transformed_net,
                        final_end_net,
                    ):
                        if is_isomorphic(transformed_net, final_end_net):
                            transformation_sequence.append(
                                (place_transformation, place),
                            )
                            logging.info(
                                f"The nets are isomorphic (P) after {transformation_sequence}.",
                            )
                            view_petri_net(transformed_net)
                            return True, transformation_sequence
                        # if not, add the new net to the queue and save what transformation was applied
                        queue.append(
                            (
                                transformed_net,
                                [
                                    *transformation_sequence,
                                    (place_transformation, place),
                                ],
                            ),
                        )
                        # add the new net to the visited set
                        visited.add(unique_net_id)

            # for each transition in the current net
            for transition in current_net.transitions:
                # apply each possible transition transformation
                for transition_transformation in transition_transformations:
                    # Note: ensures that subsequent transformations are applied to a fresh instance of the net.
                    net_copy = current_net.__deepcopy__()

                    # create a new net
                    transformed_net = transition_transformation.refine(
                        transition,
                        net_copy,
                    )
                    # generate a unique id for the new net
                    unique_net_id = generate_unique_id(transformed_net)

                    # check if the new net is the one we are looking for
                    if unique_net_id not in visited and is_valid(
                        transformed_net,
                        final_end_net,
                    ):
                        if is_isomorphic(transformed_net, final_end_net):
                            transformation_sequence.append(
                                (transition_transformation, transition),
                            )
                            logging.info(
                                f"The nets are isomorphic (T) after {transformation_sequence}.",
                            )
                            view_petri_net(transformed_net)
                            return True, transformation_sequence
                        # if not, add the new net to the queue and save what transformation was applied
                        queue.append(
                            (
                                transformed_net,
                                [
                                    *transformation_sequence,
                                    (transition_transformation, transition),
                                ],
                            ),
                        )
                    # add the new net to the visited set
                    visited.add(unique_net_id)

    # If no sequence of transformations leads to the target net
    logging.info("No sequence of transformations leads to the target net.")
    return False, []


def get_canonical_representation(petri_net: PetriNet) -> str:
    """
    Converts the Petri net to a canonical string representation.

    Args:
        petri_net (PetriNet): The Petri net object.

    Returns:
        str: Canonical string representation of the Petri net.
    """
    # Extract places, transitions, and arcs
    places = sorted(petri_net.places, key=lambda p: p.name)
    transitions = sorted(petri_net.transitions, key=lambda t: t.name)
    arcs = sorted((arc.source.name, arc.target.name) for arc in petri_net.arcs)

    # Create a dictionary with sorted elements
    net_representation = {
        "places": [place.name for place in places],
        "transitions": [trans.name for trans in transitions],
        "arcs": arcs,
    }

    # Convert dictionary to a JSON string
    return json.dumps(net_representation, separators=(",", ":"), sort_keys=True)


def generate_unique_id(petri_net: PetriNet) -> str:
    """
    Generates a unique identifier for the given Petri net.

    Args:
        petri_net (PetriNet): The Petri net object.

    Comments:
        - If you deepcopies the net, the memory id is not the same anymore

    Returns:
        str: Unique identifier for the Petri net.
    """
    # Get the canonical representation of the Petri net
    canonical_representation = get_canonical_representation(petri_net)

    # Generate a hash of the canonical representation
    return hashlib.sha256(canonical_representation.encode("utf-8")).hexdigest()


def replace() -> None:
    """Not Needed with update Implementation."""


def compositional_discovery(
    input_log_path: str,
    algorithm: callable,
    interface_pattern: BaseInterfacePattern,
    transformations: list[BaseTransformation],
    agent_column: str = "org:resource",
    **algorithm_kwargs: dict,
) -> PetriNet:
    """Compositional Process Discovery Algorithm as described in Algorithm 1.

    Args:
        input_log_path (str): The path to the event log.
        algorithm (callable): The process discovery algorithm to use.
        interface_pattern (BaseInterfacePattern): The interface pattern to use that consists of A1,...An Agents.
        transformations (list[BaseTransformation]): The list of transformations
        agent_column (str): The column in the event log that contains the agent names.
        algorithm_kwargs (dict): Additional arguments to pass to the algorithm.

    Comments:
        - Assumptions: 1. Identified IP, 2. Prepared log with transactions a!?, b!?,... 3. ...
        - Only checks Agent 1 for IP-Agent 1 and not the other agents (no nested for loop).
        - Time Complexity: ...

    Returns:
        multi_agent_net (Petri net): a multi-agent system GWF-net.
    """
    # Extract the directory and the base filename
    directory = Path(input_log_path).parent
    filename = Path(input_log_path).name

    # discover the multi-agent system net
    df_log = read_xes(input_log_path)

    # unique agents:
    unique_agents = df_log[agent_column].unique()

    # Note: No Replace. Build Late -> dict to store the discovered nets for each agent
    subnets = {}

    # Itherate through the agents
    with tqdm(total=len(unique_agents), desc="Processing Agents") as pbar:
        # for each agent in the event log
        for i, agent in enumerate(unique_agents):
            # create sub-logs
            df_log_agent = df_log[df_log[agent_column] == agent]

            # create a path to save the log file
            modified_log_path = Path(directory) / f"agent_{i+1}_{filename}"
            write_xes(df_log_agent, modified_log_path)

            # discover net. Also have the initial and final markings.
            gwf_agent_net, _, _ = discover(
                input_log_path,
                algorithm,
                **algorithm_kwargs,
            )

            # plotting of discovered net
            logging.info(f"Discovered net for Agent {agent}")
            view_petri_net(gwf_agent_net)

            # get the corresponding interface subset pattern. Also have the initial and final markings.
            interface_subset_pattern, _, _ = interface_pattern.get_net(f"A{i+1}")
            subnets[f"A{i}"] = interface_subset_pattern

            # check if discovered net is a refinement of the interface pattern for Agent Ai
            check_refinement, transformation_list = is_refinement(
                interface_subset_pattern,
                gwf_agent_net,
                transformations,
            )

            # log the result
            logging.info(
                f"Agent {agent} is a refinement: {check_refinement} with transformations: {transformation_list}",
            )

            if check_refinement:
                # Note: Repalce functionality: Update the dictionary
                subnets[f"A{i+1}"] = gwf_agent_net

            # Update progress bar
            pbar.update(1)

    # combine the nets together
    multi_agent_net = subnets["A1"].__deepcopy__()
    for i in range(2, len(subnets)):
        copy_net = subnets[f"A{i}"].__deepcopy__()
        multi_agent_net = MergeNets.merge(multi_agent_net, copy_net)

    # final plotting
    view_petri_net(multi_agent_net)

    return multi_agent_net
