import pandas as pd
import pm4py
from pm4py.objects.petri_net.obj import PetriNet


# https://github.com/pm4py/pm4py-core/blob/release/notebooks/4_conformance_checking.ipynb
# https://github.com/pm4py/pm4py-core/blob/release/notebooks/5_advanced_examples.ipynb


"""Check conformance of your collaboration process model 
and the event log with alignment-based fitness 
    and precision as well as entropy-based fitness and precision (Entropia -empr)"""


def evaluate(
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
        - Possible Algorithms: Inductive Miner, Split Miner, Alpha Miner, Heuristic Miner, etc.
        - algorithm = pm4py.discover_petri_net_inductive # also with noise threshold
        - algorithm2 = pm4py.discover_petri_net_alpha
        - algorithm3 = pm4py.discover_petri_net_heuristics
        - algorithm4 = split_miner

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
