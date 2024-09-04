import pandas as pd
import pm4py
from interface_patterns.interface_patterns import BaseInterfacePattern
from pm4py.objects.petri_net.obj import PetriNet


# TODO: Check and more algorithms.
def discover(
    df_log: pd.DataFrame,
    algorithm: pm4py.discover_petri_net_inductive,
) -> PetriNet:
    """Discover a GWF-net (process model) for the agent using  for instance the Inductive Miner.

    Args:
        df_log: The event log for the agent as a Pandas DataFrame.
        algorithm: The process discovery algorithm to use.

    Comments:
        - See implmentation: inductive_miner.apply(log, variant=variant, parameters=parameters)

    Returns:
        The discovered Petri net model for the agent.
    """
    net, initial_marking, final_marking = algorithm(df_log)
    return net, initial_marking, final_marking


# TODO: Implement.
def is_refinement() -> None:
    """Checks if the agent GWF-net is a proper refinement of the corresponding part in the interface pattern."""
    raise NotImplementedError


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
