from typing import Dict, List, Optional, Set
from app.schemas.agent_contracts import AgentName


class TaskGraphPlanner:
    """
    Constructs a dependency-aware Directed Acyclic Graph (DAG) for multi-agent execution.
    Partitions agents into topological execution waves:
    - Agents in the same wave run concurrently in parallel.
    - Waves execute sequentially, passing minimized context forward.
    """

    # Static dependency declarations
    DEPENDENCY_MAP: Dict[AgentName, List[AgentName]] = {
        AgentName.MARKETING: [],
        AgentName.FINANCIAL: [],
        AgentName.LEGAL: [],
        AgentName.TECHNOLOGY: [],
        AgentName.ESG: [],
        AgentName.HR: [AgentName.TECHNOLOGY],
        AgentName.GTM: [
            AgentName.MARKETING,
            AgentName.FINANCIAL,
            AgentName.LEGAL,
            AgentName.TECHNOLOGY,
            AgentName.HR,
            AgentName.ESG,
        ],
        AgentName.RISK: [
            AgentName.MARKETING,
            AgentName.FINANCIAL,
            AgentName.LEGAL,
            AgentName.TECHNOLOGY,
            AgentName.HR,
            AgentName.ESG,
        ],
    }

    def build_execution_plan(
        self,
        requested_agents: Optional[List[AgentName]] = None,
    ) -> List[List[AgentName]]:
        """
        Calculates execution waves using topological sorting.
        """
        active_agents: Set[AgentName] = set(
            requested_agents if requested_agents else self.DEPENDENCY_MAP.keys()
        )

        waves: List[List[AgentName]] = []
        completed: Set[AgentName] = set()

        while active_agents:
            # Find all agents whose dependencies are fully satisfied by completed set
            current_wave = [
                agent
                for agent in active_agents
                if all(dep in completed for dep in self.DEPENDENCY_MAP.get(agent, []))
            ]

            if not current_wave:
                # Cyclic or unsatisfied dependency fallback: take remaining
                current_wave = list(active_agents)

            waves.append(current_wave)
            for agent in current_wave:
                completed.add(agent)
                active_agents.remove(agent)

        return waves
