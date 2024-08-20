# Interfaces

A specification of agent interactions is called an inter- face. It represents the key interaction-oriented viewpoints of the architecture of a multi-agent system.

![alt text](fig5.png)

## Interface Patterns

Table 3 considers interface patterns developed using ser- vice interaction patterns presented in [8]. Single transmission patterns, IP-1, IP-2, and IP-3, describe rather primitive agent interactions since a sending agent is not supposed to receive an acknowledgment from the other agent. 

Various ways of asynchronous message exchange are given in patterns IP-4, IP-5, and IP-6.

Interface pattern IP-7 describes multiple trans- mission interactions when one agent can decide to stop the exchange by sending a corresponding message to the other agent.

Multilateral interactions among three or more agents are described in IP-8. According to the specification of this pattern, one of the agents expects to receive one of sev- eral messages incoming from the other agents. Sending agents should be properly notified whether their messages are received.

Table 4 describes mixed interface patterns. They combine asynchronous and synchronous agent interactions. Patterns IP-9 and IP-10 extend pattern IP-4 such that agents synchro- nize either before or after messages are exchanged. 

Pattern IP-11 extends pattern IP-5 such that agents synchronize and exchange messages concurrently. 

Pattern IP-12 allows agents to either execute a synchronous activity or exchange mes- sages. This corresponds to an extension of pattern IP-6.

![alt text](table3.png)
