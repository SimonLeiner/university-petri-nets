# Conformance Checking

Estimation of the correspondence between an event log and a process model is the main problem in the field of conformance checking

# Task:

Check conformance of your collaboration process model and the event log with:

- alignment-based fitness and precision
- entropy-based fitness and precision (Entropia -empr). If not working, copy lib folder from https://github.com/jbpt/codebase/tree/master/jbpt-pm/entropia

# Definitions

Conformance Checking Dimensions that determine the quality of a process model:

- **Fitness:** Estimates the extend to which a process discovery model is able to replay the event log. A model perfectly fits the log if all traces in the log can be replayed by the model (Fitness of 1.0
  ). The `inductive miner` guarantees the perfect fitness (1.0) of the discovered model, i.e it can execute all traces in an event log.

- **Precision:** Evaluates the ratio between the behavior allowedby a process model and not recorded in the event log. A model with perfect precision can only execute traces in an event log. The perfect precision limits the use of a process model since an event log represents only a finite snapshot of all possible process executions.

- **Generalization:** Dual metric with precision.

- **Simplicity:** Captures the complexity of a discovered model.

# Additional Clafirications:

- **Soundness: (Proper Termination)** A process model is sound if it can replay all traces in the event log. The `inductive miner` guarantees the soundness of the discovered model. Corollary 2:GWF-net discovered from an event log L using Algorithm 1 is sound.

- **Fitness:** is a value in the interval [0, 1] that demonstrates how well a process model can replay every trace from an event log. In the general case shown in Fig. 13, a part of an event log (unfitting traces) may not be covered by the firing sequences in a process model. The more the number of unfitting traces in L is, the lower the fitness of a process model is. By Definition 8, a process model perfectly fits an event log (fitness = 1) if it can execute all traces in this event log, i.e., there are no unfitting traces.
  Note that, by Corollary 1, GWF-nets obtained by Algo- rithm 1 perfectly fit event logs. Multi-Agent systems models perfectly fit the event log.

- **Violation of Assumption Soundness:** Apart from that, existing process discovery algorithms allow configuring the desired fitness level. It may be necessary to decrease the fitness while working with noisy and real-life event logs, where there can be missing or duplicate actions, the wrong ordering of actions, etc.

- **Precision:** is a value in the interval [0, 1] that evaluates a ratio of the behavior allowed by a process model and not allowed by an event log (unseen behavior as shown in Fig. 13). Perfectly precise models can only replay the traces present in an event log. However, an event log represents only a finite fragment of all possible process executions. That is why perfectly precise models are of very restrictive use. A well-known approach to the precision estimation, is based on aligning the firing sequences of a process model with the traces in an event log [18].
