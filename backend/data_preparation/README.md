# Data Cleanup

Since the Algorithm isn't well formulated in the paper and the method makes several key assumptions, we need to clean the data to make it suitable for the algorithm. The data cleanup process is as follows:

## Key Assumptions

1. All records in an event log have the corresponding “Agent” attribute.
2. There is a distinguished set of actions through which agents communicate via message exchange and synchro- nizations. For instance, in the event log shown in Table 1, the “decide” action is executed simultaneously by John and Pete.
3. Async Messages must have a ! or ? in the label (complement lables).
4. Sync Messages must have s in the label (same label).
