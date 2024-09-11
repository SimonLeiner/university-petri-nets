# README #

This repository contains the material used and produced during the validation of the Colliery technique by means of the Colliery tool. The event logs have been generated with this [tool](https://bitbucket.org/proslabteam/collaborativeloggenerator)

### Files summary ###

    .
    ├── "case_study_name"	# Folder for a case study
    │   ├── model.bpmn						# The original BPMN model
    │   ├── "process_name".xes				# The log of a participant 
    │   ├── collectivelog.xes				# The log of the entire collaboration
    │   ├── collaboration_discovered_"algorithm".bpmn	# The collaboration discovered by Collery using a discovery algorithm
    │   ├── petrinet_of_collaboration_discovered_"algorithm".pnml	# The Petrinet coresponding to a discovered collaboration
 
### Step-by-Step Validation ###

To reproduce the results of the validation please follow these steps. The first three steps are not mandatory, you can skip them and directly use the provided Petrinet files.

*	Launch  the logs generation with [tool](https://bitbucket.org/proslabteam/collaborativeloggenerator) giving as input a model.bpmn file. This produces the collectivelog.xes file and other .xes files named as the collaboration participants
*	Launch [Colliery](https://bitbucket.org/proslabteam/colliery_buid/src/master/) giving as input the logs file of each participant in the collaboration, and selecting the desired discovery parameters. This produces a BPMN file containing the resulting collaboration model.
*	Transform the obtained BPMN model into a Petrinet with the [ProM tool](https://www.promtools.org/) using the "Convert BPMN diagram to Petri net (control-flow)" plug-in, and merge them. 
*	Load the Petrinet file both with the collectivelog.xes file into ProM and use the "Replay log on Petri net for conformance analysis" plugin to obtain fitness value, and the "Check precision based on align-etconformance" plugin to get precision. In both cases the activity labels of the log and of the model have to be matched, please do it carefully paying attention to the names of the message start/intermediate events.