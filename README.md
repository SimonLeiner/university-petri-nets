# Petri-Nets

[![codecov](https://codecov.io/gh/SimonLeiner/python_template/graph/badge.svg?token=FYBFTW7BKB)](https://codecov.io/gh/SimonLeiner/python_template)
[![DeepSource](https://app.deepsource.com/gh/SimonLeiner/python_template.svg/?label=active+issues&show_trend=true&token=zHKCkR8ZqHwQC4IJL31TziwF)](https://app.deepsource.com/gh/SimonLeiner/python_template/)
[![Formatting](https://github.com/SimonLeiner/university-petri-nets/actions/workflows/ruff.yml/badge.svg)](https://github.com/SimonLeiner/university-petri-nets/actions/workflows/ruff.yml)

## Organisation - Project

- Individual projects to implement online process discovery (each individual project corresponds to a single discovery algorithm)
- Web service, CPEE models and subscriptions, Python backend
- Deadline latest end of semester, individually agreed with me
- Submit git respository with getting started + about 15 min of Q&A each
- Technical, e.g., algorithm, Practical, e.g., architecture, Qualitative, e.g., visualization

## Project Assignment

Develop a web application with the following functionality:

- Discover a collaboration process model with your assigned collaboration process discovery technique
- Check conformance of your collaboration process model and the event log with alignment-based fitness and precision as well as entropy-based fitness and precision (Entropia -empr)
- Visualize your discovered model (group collaboration concepts, minimize overlapping collaborations between concepts, ensure left-to-right and top-to-bottom flow) and allow interactive analysis with interaction operations: Zoom in, zoom out, focus on collaboration concept‘s process only (agent, service, partner), save current visualization to disk (as .svg
  and .pnml)

Your web interface should allow for the following configurations:

- the uploaded event log (27 event logs given)
- the process discovery technique to be applied, i.e., IM, IMf (noise_threshold), and Split miner all parameters / further input of your technique

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/SimonLeiner/quantum-scope.git
```

2. Setup the environment:

We recomment using devcontainer for development. You can find the devcontainer configuration in the `.devcontainer` folder. Adjust the configuration to your needs.

## Main Paper "Discovering architecture-aware and sound process models of multi-agent systems: a compositional approach"

- /Users/simonleiner/TUM/Master/SS_2024/PetriNetze/Task/gwf.pdf

## Other Resources

- /Users/simonleiner/TUM/Master/SS_2024/PetriNetze/lab01_2024.pdf
- /Users/simonleiner/TUM/Master/SS_2024/PetriNetze/lab02_2024.pdf
- /Users/simonleiner/TUM/Master/SS_2024/PetriNetze/lab03_2024.pdf
- /Users/simonleiner/TUM/Master/SS_2024/PetriNetze/lab04_2024.pdf

## References

- https://github.com/xflr6/graphviz
- https://www.researchgate.net/figure/Compositional-process-discovery_fig3_360352443
- https://github.com/pm4py/pm4py-core
- https://github.com/Gmod4phun/PetriNetParser
- https://github.com/Dominik-Hillmann/petrinets
