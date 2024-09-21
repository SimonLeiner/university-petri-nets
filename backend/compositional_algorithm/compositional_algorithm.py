import hashlib
import inspect
import json
import logging
import time
from collections import Counter
from pathlib import Path
from queue import PriorityQueue

import networkx as nx
import numpy as np
from networkx.algorithms import isomorphism
from pm4py import read_xes
from pm4py import view_petri_net
from pm4py import write_xes
from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from tqdm import tqdm

from compositional_algorithm.combine_nets.combine_nets import MergeNets
from compositional_algorithm.interface_patterns.interface_patterns import (
    BaseInterfacePattern,
)
from compositional_algorithm.transformations.transformations import BaseTransformation
from compositional_algorithm.transformations.transformations import PlaceTransformation
from compositional_algorithm.transformations.transformations import (
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
) -> tuple[PetriNet, Marking, Marking]:
    """Discover a GWF-net (process model) for the agent using  for instance the Inductive Miner.

    Args:
        input_log_path (str): The path to the event log.
        algorithm (callable): The process discovery algorithm to use.
        algorithm_kwargs: Additional arguments to pass to the algorithm.

    Comments:
        - Possible Algorithms: Inductive Miner, Split Miner, Alpha Miner, Heuristic Miner, etc.
        - algorithm = pm4py.discover_petri_net_inductive # also with noise threshold
        - algorithm2 = pm4py.discover_petri_net_alpha
        - algorithm3 = pm4py.discover_petri_net_heuristics
        - algorithm4 = split_miner

    Returns:
        The discovered Petri net model for the agent, initial marking, and final marking.
    """
    # Inspect the algorithm's signature
    sig = inspect.signature(algorithm)
    parameters = list(sig.parameters.values())
    first_param = parameters[0]

    # Note: check based on what the discover algorithm expects
    # Split miner needs input path
    if first_param.annotation is str:
        # keep it as it is
        log_input = input_log_path
    else:
        # Convert the input log path to a DataFrame
        log_input = read_xes(input_log_path)

    net, initial_marking, final_marking = algorithm(log_input, **algorithm_kwargs)
    return net, initial_marking, final_marking


def is_net_valid(
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
    valid = True

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

    # Check the maximum number of outgoing arcs per transition and maximum number of incoming arcs per place
    max_out_arcs_per_transition = 4
    max_in_arcs_per_place = 4

    # place out arcs is the same as place in arcs
    transition_out_arcs = {transition: 0 for transition in current_net.transitions}
    place_in_arcs = {place: 0 for place in current_net.places}
    place_out_arcs = {place: 0 for place in current_net.places}

    for arc in current_net.arcs:
        if isinstance(arc.source, PetriNet.Transition):
            transition_out_arcs[arc.source] += 1
        if isinstance(arc.target, PetriNet.Place):
            place_in_arcs[arc.target] += 1
        if isinstance(arc.source, PetriNet.Place):
            place_out_arcs[arc.source] += 1
        if isinstance(arc.target, PetriNet.Transition):
            # Transition incoming arcs are not directly counted, they are accounted by the target being a transition
            pass

    for out_arcs in transition_out_arcs.values():
        if out_arcs > max_out_arcs_per_transition:
            valid = False
            break

    for in_arcs in place_in_arcs.values():
        if in_arcs > max_in_arcs_per_place:
            valid = False
            break

    # temination factor
    still_valid = (
        len(current_net.places) <= len(end_net.places)
        and len(current_net.transitions) <= len(end_net.transitions)
        and len(current_net.arcs) <= len(end_net.arcs)
    )

    # only a certain number of places, transitions and arcs
    return valid and still_valid


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


def shannon_entropy(array: np.ndarray) -> float:
    """Calculates the Shannon entropy of the given array."""
    total = np.sum(array)
    probs = array / total
    return -np.sum([p * np.log2(p) for p in probs if p > 0])


def priority_identifier(
    net1: PetriNet,
    net2: PetriNet,
    transformation_sequence: list[tuple[BaseTransformation, PetriNet.Place]],
) -> int:
    """Calculates the priority of the Petri nets.

    Args:
        net1 (PetriNet): The first Petri net.
        net2 (PetriNet): The second Petri net.
        transformation_sequence (list): The sequence of transformations that lead to the target.

    Comments:
        - Minimize Distance between nets. The more negative the value, the more similar the nets are.
        - Transitions are more important than places.
        - The transformation have an Information gain of P1:5->8, P2:5->8, P3:5->9, P4:7->9. Hence I fonly using diff, always takes P3.
        - Range: [0, log(n)] Maximum entropy is achieved when all classes have equal counts.

    Returns:
        int: The priority of the Petri nets.
    """
    # Note: Equality. The less the better.
    # transformation difference (total number of transformations): Opt is 0
    transitions_net1 = len(net1.transitions)
    transitions_net2 = len(net2.transitions)
    transition_diff = abs(transitions_net1 - transitions_net2)

    # place difference (total number of places): Opt is 0
    places_net1 = len(net1.places)
    places_net2 = len(net2.places)
    place_diff = abs(places_net1 - places_net2)

    # arcs difference (total number of arcs): Opt is 0
    arcs_net1 = len(net1.arcs)
    arcs_net2 = len(net2.arcs)
    arcs_diff = abs(arcs_net1 - arcs_net2)

    # some kind of normalized net difference (the lower the better -> the more similar the nets are)
    net_total_diff = transition_diff + place_diff + arcs_diff
    net_diff = np.log2(net_total_diff)

    # Note: Diversity. The More the better.
    # Class Diversity - check how many unique classes there are
    class_types = [item[0] for item in transformation_sequence]
    class_counts = Counter(class_types)
    class_counts = np.array(list(class_counts.values()))
    class_diversity = shannon_entropy(class_counts)

    # Parameter Diversity - assuming the parameters are strings, let's count distinct parameters
    params = [item[1] for item in transformation_sequence]
    param_counts = Counter(params)
    param_counts = np.array(list(param_counts.values()))
    param_diversity = shannon_entropy(param_counts)

    # Get the current time since the epoch in milliseconds
    unique_offset = int(time.time() * 1000000000) % 1000000 * 1e-9

    return net_diff - class_diversity - param_diversity + unique_offset


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
        - Transformations first -> deeper net vs. places first -> wider net.
        - Use Min-heap, meaning it always retrieves the smallest item based on the priority value as queue implementation for faster search.
        - The priority queue has O(log n) time complexity for insertion and O(1) time complexity for retrieval.

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

    # Handle empty transformations list
    if not place_transformations and not transition_transformations:
        logging.info("No transformations provided.")
        return False, []

    # Create a queue for BFS and add the initial net.
    priority_queue = PriorityQueue()
    priority_queue.put((priority_identifier(first_net, final_end_net), first_net, []))

    # Initialize the set of visited states
    visited = set()
    visited.add(generate_unique_id(first_net))

    # counter for plotting
    counter = 0

    # as long as there is an element in the queue
    with tqdm(total=None, desc="Processing Queue") as pbar:
        while priority_queue:
            # Update progress bar
            pbar.update(1)

            # dequeue the first element in the queue
            priority, current_net, transformation_sequence = priority_queue.get()

            # plotting of discovered net every 1000 iterations
            if counter % 1000 == 0:
                logging.info(
                    f"Discovering new net ({int(priority)} priority, {len(current_net.places)} places, {len(current_net.transitions)} transitions, {len(current_net.arcs)} arcs).",
                )
                view_petri_net(current_net, format="png")

            # Note: branching logic: we need to apply all possible transformations
            # for each place in the current net
            for place in current_net.places:
                # apply each possible place transformation
                for place_transformation in place_transformations:
                    # Note: Deep copy of the current net before applying the transformation -> transformation change places & transitions and sets are immutable.
                    net_copy = current_net.__deepcopy__()
                    transformed_net = place_transformation.refine(place, net_copy)
                    unique_net_id = generate_unique_id(transformed_net)
                    transformation_sequence_element = (place_transformation, place)

                    # check if the new net is the one we are looking for
                    if unique_net_id not in visited and is_net_valid(
                        transformed_net,
                        final_end_net,
                    ):
                        if is_isomorphic(transformed_net, final_end_net):
                            transformation_sequence.append(
                                transformation_sequence_element,
                            )
                            logging.info(
                                f"The nets are isomorphic (P) after {transformation_sequence}.",
                            )
                            return True, transformation_sequence
                        # if not, add the new net to the queue and save what transformation was applied
                        priority_queue.put(
                            (
                                priority_identifier(transformed_net, final_end_net),
                                transformed_net,
                                [
                                    *transformation_sequence,
                                    transformation_sequence_element,
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
                    transformed_net = transition_transformation.refine(
                        transition,
                        net_copy,
                    )
                    unique_net_id = generate_unique_id(transformed_net)
                    transformation_sequence_element = (
                        transition_transformation,
                        transition,
                    )

                    # check if the new net is the one we are looking for
                    if unique_net_id not in visited and is_net_valid(
                        transformed_net,
                        final_end_net,
                    ):
                        if is_isomorphic(transformed_net, final_end_net):
                            transformation_sequence.append(
                                transformation_sequence_element,
                            )
                            logging.info(
                                f"The nets are isomorphic (T) after {transformation_sequence}.",
                            )
                            return True, transformation_sequence
                        # if not, add the new net to the queue and save what transformation was applied
                        priority_queue.put(
                            (
                                priority_identifier(transformed_net, final_end_net),
                                transformed_net,
                                [
                                    *transformation_sequence,
                                    transformation_sequence_element,
                                ],
                            ),
                        )
                        # add the new net to the visited set
                        visited.add(unique_net_id)

            # Update counter
            counter += 1

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
            logging.info(
                f"Discovered net for Agent {agent} ({len(gwf_agent_net.places)} places, {len(gwf_agent_net.transitions)} transitions, {len(gwf_agent_net.arcs)} arcs).",
            )
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
    for i in range(2, len(subnets) + 1):
        copy_net = subnets[f"A{i}"].__deepcopy__()
        multi_agent_net = MergeNets.merge_nets(multi_agent_net, copy_net)

    # final plotting
    logging.info(
        f"Discovered compositional net ({len(gwf_agent_net.places)} places, {len(gwf_agent_net.transitions)} transitions, {len(gwf_agent_net.arcs)} arcs).",
    )
    view_petri_net(multi_agent_net)

    return multi_agent_net
