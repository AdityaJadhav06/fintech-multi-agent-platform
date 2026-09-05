import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from app.schemas.agent_contracts import (
    AgentName,
    AgentState,
    AgentInputContract,
    AgentOutputContract,
)
from app.agents import create_agent
from app.orchestrator.planner import TaskGraphPlanner


class OrchestratorExecutor:
    """
    Executes the multi-agent task graph with:
    - Parallel wave concurrency via asyncio
    - Context minimization (least privilege data filtering)
    - Fault isolation (failed agents do not abort entire execution)
    - Real-time progress event callbacks (for SSE streaming)
    """

    def __init__(self, planner: Optional[TaskGraphPlanner] = None):
        self.planner = planner or TaskGraphPlanner()

    def filter_minimized_context(
        self,
        target_agent: AgentName,
        all_completed_outputs: Dict[AgentName, AgentOutputContract],
    ) -> List[Dict[str, Any]]:
        """
        Applies context minimization:
        Only forwards upstream findings that are strictly relevant to the target agent.
        """
        minimized = []

        if target_agent == AgentName.HR:
            # HR only needs tech role findings
            if AgentName.TECHNOLOGY in all_completed_outputs:
                tech_out = all_completed_outputs[AgentName.TECHNOLOGY]
                minimized.append({
                    "agent": tech_out.agent.value,
                    "summary": tech_out.summary,
                    "calculations": tech_out.calculations,
                })

        elif target_agent in (AgentName.GTM, AgentName.RISK):
            # GTM and Risk receive high-level summaries and risks from all prior agents
            for agent_name, out in all_completed_outputs.items():
                minimized.append({
                    "agent": out.agent.value,
                    "summary": out.summary,
                    "findings": [f.model_dump() for f in out.findings],
                    "risks": [r.model_dump() for r in out.risks],
                    "human_review_required": out.human_review_required,
                })

        elif target_agent == AgentName.FINANCIAL:
            # Financial incorporates Tech cloud costs and Marketing CAC
            for dep in (AgentName.TECHNOLOGY, AgentName.MARKETING):
                if dep in all_completed_outputs:
                    out = all_completed_outputs[dep]
                    minimized.append({
                        "agent": out.agent.value,
                        "summary": out.summary,
                        "calculations": out.calculations,
                    })

        return minimized

    async def execute_case(
        self,
        case_id: str,
        org_id: str,
        user_request: str,
        business_context: str,
        constraints: Dict[str, Any],
        document_refs: List[str],
        requested_agents: Optional[List[AgentName]] = None,
        event_callback: Optional[Callable[[str, AgentName, AgentState, Optional[str]], None]] = None,
    ) -> Dict[AgentName, AgentOutputContract]:
        """
        Executes the plan wave-by-wave and returns all agent outputs.
        """
        waves = self.planner.build_execution_plan(requested_agents)
        completed_outputs: Dict[AgentName, AgentOutputContract] = {}

        for wave_idx, wave in enumerate(waves, start=1):
            tasks = []
            for agent_name in wave:
                if event_callback:
                    event_callback(case_id, agent_name, AgentState.RUNNING, f"Wave {wave_idx}: Started analysis.")

                # Prepare minimized input contract
                upstream_ctx = self.filter_minimized_context(agent_name, completed_outputs)
                contract = AgentInputContract(
                    case_id=case_id,
                    org_id=org_id,
                    user_request=user_request,
                    business_context=business_context,
                    document_refs=document_refs,
                    constraints=constraints,
                    requested_task=f"Perform domain analysis as {agent_name.value}",
                    upstream_findings=upstream_ctx,
                )

                agent_instance = create_agent(agent_name)
                tasks.append(self._safe_execute_agent(agent_instance, contract, event_callback))

            # Concurrently execute all agents in this wave
            results = await asyncio.gather(*tasks)

            for agent_name, output in zip(wave, results):
                completed_outputs[agent_name] = output

        return completed_outputs

    async def _safe_execute_agent(
        self,
        agent_instance,
        contract: AgentInputContract,
        event_callback: Optional[Callable[[str, AgentName, AgentState, Optional[str]], None]],
    ) -> AgentOutputContract:
        """
        Executes an agent with error isolation so one failure never halts the DAG.
        """
        try:
            output = await agent_instance.run(contract)
            if event_callback:
                event_callback(contract.case_id, agent_instance.name, output.status, output.summary)
            return output
        except Exception as e:
            failed_output = AgentOutputContract(
                agent=agent_instance.name,
                case_id=contract.case_id,
                status=AgentState.FAILED,
                summary=f"Execution error: {str(e)}",
                findings=[],
                calculations={},
                assumptions=[],
                data_gaps=[f"Agent failed with exception: {str(e)}"],
                risks=[],
                dependencies=[],
                sources=[],
                human_review_required=True,
                review_reasons=[f"Agent {agent_instance.name.value} crashed during execution."],
                timestamp=datetime.utcnow(),
            )
            if event_callback:
                event_callback(contract.case_id, agent_instance.name, AgentState.FAILED, str(e))
            return failed_output
