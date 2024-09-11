from collections import deque

import networkx as nx
import pandas as pd
from interface_patterns.interface_patterns import BaseInterfacePattern
from networkx.algorithms import isomorphism
from pm4py.objects.petri_net.obj import PetriNet


def discover(
    df_log: pd.DataFrame,
    algorithm: callable,
    **algorithm_kwargs,  # noqa: ANN003
) -> PetriNet:
    """Discover a GWF-net (process model) for the agent using  for instance the Inductive Miner.

    Args:
        df_log (pd.DataFrame): The event log for the agent.
        algorithm (callable): The process discovery algorithm to use.
        algorithm_kwargs: Additional arguments to pass to the algorithm.

    Comments:
        - See implmentation: inductive_miner.apply(log, variant=variant, parameters=parameters)

    Returns:
        The discovered Petri net model for the agent.
    """
    net, initial_marking, final_marking = algorithm(df_log, algorithm_kwargs)
    return net, initial_marking, final_marking


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


# TODO: Correct Implementation.
def is_refinement(
    initial_net: PetriNet,
    target_net: PetriNet,
    transformations: list,
) -> bool:
    """Checks if the agent GWF-net is a proper refinement of the corresponding part in the interface pattern.

    Args:
        initial_net (PetriNet): The agent GWF-net.
        target_net (PetriNet): The corresponding part in the interface pattern.
        transformations (list): The list of transformations to apply.

    Comments:
        -  We use BFS to find a sequence of transformations that transforms the input net into the target net.

    Returns:
        bool: True if the agent GWF-net is a proper refinement of the corresponding part in the interface pattern.
    """
    # Create a queue for BFS and add the initial net
    queue = deque([(initial_net, [])])

    # To keep track of visited states
    visited = set()

    while queue:
        current_net, transformation_sequence = queue.popleft()

        # Check if the current net is isomorphic to the target net
        if is_isomorphic(current_net, target_net):
            return True

        # Mark the current net as visited (you may need a hashable form of the net)
        visited.add(
            id(current_net),
        )  # Use `id` to track visited Petri nets by object reference

        # Apply each of the 4 transformations
        for transformation in transformations:
            new_net = transformation(current_net)

            # If the new net hasn't been visited, add it to the queue
            if id(new_net) not in visited:
                queue.append((new_net, [*transformation_sequence, transformation]))

    # If no transformation sequence leads to the target net
    return False


# TODO: Implement.
def replace() -> None:
    """Substitutes the agent GWF-net with the corresponding part in the interface pattern."""
    raise NotImplementedError


# TODO: Check Implementation.
def compositional_discovery(
    df_log: pd.Dataframe,
    interface_pattern: BaseInterfacePattern,
    agent_column: str = "org:resource",
) -> PetriNet:
    """Compositional Process Discovery Algorithm as described in Algorithm 1.

    Args:
        df_log (pd.DataFrame): The event log for the multi-agent system.
        interface_pattern (BaseInterfacePattern): The interface pattern to use.
        agent_column (str): The column in the event log that contains the agent names.

    Comments:
        - Merge or compose the nets according to your specific composition rules.
            composed_net = pm4py.algo.conformance.alignments.petri_net.composer.compose(
                [composed_net, net],
            )

    Returns:
        multi_agent_net (Petri net): a multi-agent system GWF-net.
    """
    # store the agent gwf-nets in a set
    discovered_nets = {}

    # init multi agent system gwf net
    multi_agent_net = interface_pattern

    # construct agent models
    for agent in df_log[agent_column].unique():
        # create sub-logs and discover gwf-nets and add to discovered_nets
        df_log_agent = df_log[df_log[agent_column] == agent]
        net, _, _ = discover(df_log_agent)
        discovered_nets.add(net)

    # for each agent model
    for net in discovered_nets:
        # check if the agent model is a refinement of the interface pattern
        if is_refinement(net):
            # substitute the agent model with the corresponding part in the interface pattern
            replace(net, multi_agent_net)

    return multi_agent_net


def filter_logs_by_agent(
    df_log: pd.DataFrame,
    agent_column: str = "org:resource",
) -> dict:
    """
    Construct a set of sub-logs for each agent in the event log.

    Args:
        df_log: A pandas DataFrame where each row represents an event.
        agent_column: The name of the column that contains the agent identifier.

    Comments:
        - Step 1: Event Log Filtering Function
        - An event log of a multi-agent system is filtered by actions executed by different agents. Correspondingly, we construct a set of sub-logs. For instance, filtering the records in the event log given in Table 1 by the “Pete” value of the “Agent” attribute, we obtain the sub-log presented in Table 2.
        - pm4py.filter_event_attribute_values

    Returns:
        A dictionary where each key is an agent identifier and the corresponding value is a sub-log of the
    """
    # subset the log by agent and store in a dictionary
    agent_logs = {}
    for agent in df_log[agent_column].unique():
        agent_logs[agent] = df_log[df_log[agent_column] == agent]
    return agent_logs
