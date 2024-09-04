import pandas as pd
import pm4py
from pm4py.objects.petri_net.obj import PetriNet


# TODO: Implement conformance checking methods


def check_replay(net: PetriNet, df_log: pd.DataFrame) -> bool:
    """
    Validates the composed model by checking if it can execute all traces in the original log.

    Args:
        net (PetriNet): The composed Petri net model.
        df_log (pd.DataFrame): The original event log.

    Returns:
        True if the model is valid, otherwise False.
    """
    # You can use conformance checking methods like token-based replay or alignment-based replay
    fitness = pm4py.algo.conformance.tokenreplay.factory.apply(
        df_log,
        net,
    )
    # According to the first correctnes theorem the net must replay all traces in the event logs.
    return fitness["trace_fitness"] == 1.0
