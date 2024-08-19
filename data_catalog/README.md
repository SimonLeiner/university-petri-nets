# Data

Compositional discovery of architecture-aware and sound process models from event logs of multi-agent systems: experimental data.

## Description

This repository contains the experimental data used for the evaluation of the compositional approach to the discovery of process models from event logs of multi-agent systems, where agents interact according to specific patterns of synchronous and asynchronous interactions.

According to the experiment plan, there is the folder for each interface pattern containing:

The reference model (Petri net encoded in PNML-file)
The event log obtained by simulating the behavior of the reference model (XES-file)
The model discovered directly from the generated event log (Petri net encoded in PNML-file)
The model discovered by composing the agent model w.r.t. the interface pattern (Petri net encoded in PNML-file)

## References

- https://zenodo.org/records/5830863
- https://dl.acm.org/doi/10.1007/s10270-022-01008-x
- https://bitbucket.org/proslabteam/colliery_validation/src/master/
- https://www.researchgate.net/publication/378548791_A_technique_for_discovering_BPMN_collaboration_diagrams
- https://github.com/Lihuiling12/TASE
- https://ieeexplore.ieee.org/document/9849433
