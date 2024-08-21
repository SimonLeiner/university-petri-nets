import pandas as pd


def filter_logs_by_agent(event_log: pd.DataFrame, agent_column: str = "agent") -> dict:
    """
    Filters the event log into sub-logs for each agent.

    Args:
        event_log: A pandas DataFrame where each row represents an event.
        agent_column: The name of the column that contains the agent identifier.

    Comments:
        - First Step in the Compositional Algorithm.
        - An event log of a multi-agent system is filtered by actions executed by different agents. Correspondingly, we construct a set of sub-logs. For instance, filtering the records in the event log given in Table 1 by the “Pete” value of the “Agent” attribute, we obtain the sub-log presented in Table 2.

    Returns:
        A dictionary where each key is an agent identifier and the corresponding value is a sub-log of the
    """
    agent_logs = {}
    for trace in event_log:
        for event in trace:
            agent = event[agent_column]
            if agent not in agent_logs:
                agent_logs[agent] = []
            agent_logs[agent].append(trace)

    return agent_logs
