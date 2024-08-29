import pandas as pd


def filter_logs_by_agent(
    df_log: pd.DataFrame,
    agent_column: str = "org:resource",
) -> dict:
    """
    Construct a set of sub-logs for each agent in the event log.

    Args:
        df_log: A pandas DataFrame where each row represents an event.
        agent_column: The name of the column that contains the agent identifier.

    Comments:
        - Step 1: Event Log Filtering Function
        - An event log of a multi-agent system is filtered by actions executed by different agents. Correspondingly, we construct a set of sub-logs. For instance, filtering the records in the event log given in Table 1 by the “Pete” value of the “Agent” attribute, we obtain the sub-log presented in Table 2.

    Returns:
        A dictionary where each key is an agent identifier and the corresponding value is a sub-log of the
    """
    # subset the log by agent and store in a dictionary
    agent_logs = {}
    for agent in df_log[agent_column].unique():
        agent_logs[agent] = df_log[df_log[agent_column] == agent]
    return agent_logs
