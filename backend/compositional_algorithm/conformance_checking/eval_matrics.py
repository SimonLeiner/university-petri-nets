import pandas as pd
import pm4py
from pm4py.objects.petri_net.obj import PetriNet


# TODO: Implement conformance checking methods. See: https://processintelligence.solutions/static/api/2.7.11/api.html#conformance-checking-pm4py-conformance
"""# from pm4py.algo.conformance.alignments.metrics import fitness
# from pm4py.algo.conformance.alignments.metrics import precision
# from pm4py.algo.discovery.bpmn import algorithm as bpmn_discovery
# from pm4py.objects.log.importer.xes import importer as xes_importer


# # Load event log and process model
# log = xes_importer.apply("path/to/your/event_log.xes")
# model = bpmn_discovery.apply(log)

# # Calculate alignment-based fitness
# fitness_score = fitness.apply(log, model)
# print(f"Alignment-Based Fitness: {fitness_score}")

# # Calculate alignment-based precision
# precision_score = precision.apply(log, model)
# print(f"Alignment-Based Precision: {precision_score}")"""


def check_soundness(net: PetriNet) -> bool:
    """
    Validates the composed model by checking if it is sound.

    Args:
        net (PetriNet): The composed Petri net model.

    Comments:
        - Corollary 2: "GWF-net discovered from an event log L using Algorithm 1 is sound."
        - pm4py.objects.petri.check_soundness.check_easy_soundness_of_wfnet(net)
        - pm4py.objects.petri.check_soundness.check_easy_soundness_net_in_fin_marking
        - pm4py.objects.petri.check_soundness.check_wfnet
        - pm4py.analysis.check_is_workflow_net
        - pm4py.analysis.check_soundness

    Returns:
        True if the model is valid, otherwise False.
    """
    return pm4py.analysis.petrinet.soundness.check_soundness(net)


def check_fitness(net: PetriNet, df_log: pd.DataFrame) -> bool:
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
