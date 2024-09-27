import sys  # noqa: INP001


sys.path.append("/app/backend")

from entropy_conformance.entropy_conformance import entropy_conformance


# Note: Bit Tricky, since requires unsupported Java 8. Needs local paths, can't deal with github paths, download the files.
# entropy based fitness and precision for their example logs
precision, recall = entropy_conformance(
    "https://github.com/jbpt/codebase/blob/master/jbpt-pm/entropia/examples/log1.xes",
    "https://github.com/jbpt/codebase/blob/master/jbpt-pm/entropia/examples/model1.pnml",
)
print(f"Precision: {precision}, Recall: {recall}")  # noqa: T201


# Note: runs easily in a .py file. Bit Tricky, since requires unsupported Java 8.
# entropy based fitness and precision
precision, recall = entropy_conformance(
    "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-1/IP-1_initial_log.xes",
    "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-1/IP-1_directly_mined.pnml",
)
print(f"Precision: {precision}, Recall: {recall}")  # noqa: T201
