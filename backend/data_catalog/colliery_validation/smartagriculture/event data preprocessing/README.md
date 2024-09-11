# COLLIERY Multi-Robot Data Preprocessing
This repository contains the script that perform the preprocessing steps of data produced by a multi-robot system

```
.
├── in_log/                         # Event logs produced by each robot
├── communication_processing.py     # Generates the MRS event log enriched with communication details
├── dependencies.json               # Dependency graph between ROS nodes and topics
├── merge.py                        # Implements the event log merging
├── MRS_coll.csv                    # MRS event log with communication details
├── MRS.csv                         # MRS event log without communication details
└── README.md
```


# Run
```bash
python merge.py
python communication_processing.py
```