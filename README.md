# Petri-Nets

[![codecov](https://codecov.io/gh/SimonLeiner/university-petri-nets/graph/badge.svg?token=ylPOjFIKvY)](https://codecov.io/gh/SimonLeiner/university-petri-nets)
[![DeepSource](https://app.deepsource.com/gh/SimonLeiner/university-petri-nets.svg/?label=active+issues&show_trend=true&token=A94lUpOHD7gzUx7a7331vgmz)](https://app.deepsource.com/gh/SimonLeiner/university-petri-nets/)
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

**Clone the repository:**

```bash
git clone https://github.com/SimonLeiner/university-petri-nets.git
```

**Setup the environment:**

- We recomment using devcontainer for development. You can find the devcontainer configuration in the appropriate `.devcontainer` folders. Adjust the configuration to your needs.

CD into the project directory and run the following command:

```
docker compose up -d
```

Ensure that the containers are up and running:

```
docker compose ps
```

If you make changes to the Dockerfile or dependencies, rebuild the containers with:

```
docker compose up --build -d
```

## Main Paper "Discovering architecture-aware and sound process models of multi-agent systems: a compositional approach"

- https://data.niaid.nih.gov/resources?id=zenodo_5830862

## Other Resources

- Lab Course Files

## References

- https://github.com/xflr6/graphviz
- https://www.researchgate.net/figure/Compositional-process-discovery_fig3_360352443
- https://github.com/pm4py/pm4py-core
- https://github.com/Gmod4phun/PetriNetParser
- https://github.com/Dominik-Hillmann/petrinets
- ...
