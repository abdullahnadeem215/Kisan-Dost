"""
Core OpenAI Agents SDK primitives and provider-agnostic Runner for Kisan Dost.
Defines Agent, Runner, function_tool, Handoff, and RunResult objects.
Supports Groq LLM client fallback when OpenAI API key is absent.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, Callable, Union
from pydantic import BaseModel, Field
from config.settings import settings
from app.integrations.groq_client import GroqClient
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt
from app.schemas.conflict import DataConflictResolution
from app.schemas.evidence import Evidence

logger = logging.getLogger(__name__)


class FunctionTool:
    """
    Wrapper around python functions for agent execution.
    """
    def __init__(self, fn: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.fn = fn
        self.name = name or fn.__name__
        self.description = description or (fn.__doc__.strip() if fn.__doc__ else self.name)
        self.__doc__ = self.description

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def function_tool(fn: Optional[Callable] = None, *, name: Optional[str] = None, description: Optional[str] = None):
    """
    Decorator or factory to transform a Python function into an Agents SDK FunctionTool.
    """
    if fn is None:
        def decorator(f: Callable) -> FunctionTool:
            return FunctionTool(f, name=name, description=description)
        return decorator
    return FunctionTool(fn, name=name, description=description)


class Handoff:
    """
    Represents an explicit Agent Handoff route with transfer rationale and target agent.
    """
    def __init__(self, target: Any, description: Optional[str] = None, intent: Optional[str] = None):
        self.target = target
        self.description = description or f"Handoff to {getattr(target, 'name', str(target))}"
        self.intent = intent or getattr(target, 'name', str(target)).lower()


def handoffs(*targets: Union[Any, Handoff]) -> List[Handoff]:
    """
    Constructs a list of Handoff instances from target agents or handoffs.
    """
    result = []
    for t in targets:
        if isinstance(t, Handoff):
            result.append(t)
        else:
            result.append(Handoff(target=t))
    return result


class Agent:
    """
    OpenAI Agents SDK Agent representation.
    Holds agent name, system instructions, function tools, handoffs, and LLM model identifier.
    """
    def __init__(
        self,
        name: str,
        instructions: str,
        tools: Optional[List[Union[FunctionTool, Callable]]] = None,
        handoffs: Optional[List[Union['Agent', Handoff]]] = None,
        model: Optional[str] = None
    ):
        self.name = name
        self.instructions = instructions
        self.model = model or settings.groq_model

        self.tools: List[FunctionTool] = []
        if tools:
            for t in tools:
                if isinstance(t, FunctionTool):
                    self.tools.append(t)
                elif callable(t):
                    self.tools.append(FunctionTool(t))

        self.handoffs: List[Handoff] = []
        if handoffs:
            for h in handoffs:
                if isinstance(h, Handoff):
                    self.handoffs.append(h)
                else:
                    self.handoffs.append(Handoff(target=h))

    def get_tool(self, name: str) -> Optional[FunctionTool]:
        for tool in self.tools:
            if tool.name.lower() == name.lower():
                return tool
        return None


class RunResult(BaseModel):
    """
    Aggregated execution result produced by Runner across agent handoffs and tool calls.
    """
    final_output: str = Field(...)
    agent_history: List[str] = Field(default_factory=list)
    specialist_outputs: List[Dict[str, Any]] = Field(default_factory=list)
    decision: Optional[AgronomicDecision] = None
    receipt: Optional[DecisionReceipt] = None
    conflicts: List[DataConflictResolution] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True
    }


class Runner:
    """
    OpenAI Agents SDK Runner orchestrating agent tool executions, multi-agent handoffs,
    and provider-agnostic model routing (Groq / OpenAI API).
    """

    @classmethod
    def run(
        cls,
        agent: Agent,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RunResult:
        """
        Executes an agent workflow starting at `agent` with given `input_text` and `context`.
        Handles intent routing, specialist tool invocations, agent handoffs, and synthesis.
        """
        context = context or {}
        agent_history: List[str] = [agent.name]
        specialist_outputs: List[Dict[str, Any]] = context.get("specialist_outputs", [])

        # Check if starting at Triage Agent or an Agent with handoffs
        if agent.name.lower().startswith("triage"):
            from app.agents.triage import analyze_intents
            from app.agents.agronomy import agronomy_agent, run_agronomy_agent
            from app.agents.pest_doctor import pest_doctor_agent, run_pest_doctor_agent
            from app.agents.market import market_agent, run_market_agent
            from app.agents.finance_govt import finance_govt_agent, run_finance_govt_agent
            from app.agents.synthesis import synthesis_agent, run_synthesis_agent

            intents = analyze_intents(input_text)
            logger.info(f"Triage agent identified intents: {intents}")

            if "agronomy" in intents:
                agent_history.append(agronomy_agent.name)
                res = run_agronomy_agent(input_text, context)
                specialist_outputs.append(res)

            if "pest" in intents:
                agent_history.append(pest_doctor_agent.name)
                res = run_pest_doctor_agent(input_text, context)
                specialist_outputs.append(res)

            if "market" in intents:
                agent_history.append(market_agent.name)
                res = run_market_agent(input_text, context)
                specialist_outputs.append(res)

            if "finance_govt" in intents:
                agent_history.append(finance_govt_agent.name)
                res = run_finance_govt_agent(input_text, context)
                specialist_outputs.append(res)

            # If no specific intent matched, default to agronomy
            if not specialist_outputs:
                agent_history.append(agronomy_agent.name)
                res = run_agronomy_agent(input_text, context)
                specialist_outputs.append(res)

            # Perform Handoff to Synthesis Agent
            agent_history.append(synthesis_agent.name)
            synthesis_res = run_synthesis_agent(
                query_text=input_text,
                specialist_outputs=specialist_outputs,
                farmer_profile=context.get("farmer_profile")
            )

            return RunResult(
                final_output=synthesis_res["markdown"],
                agent_history=agent_history,
                specialist_outputs=specialist_outputs,
                decision=synthesis_res.get("decision"),
                receipt=synthesis_res.get("receipt"),
                conflicts=synthesis_res.get("conflicts", []),
                evidence=synthesis_res.get("evidence", [])
            )

        # Single specialist agent run
        elif agent.name.lower().startswith("agronomy"):
            from app.agents.agronomy import run_agronomy_agent
            out = run_agronomy_agent(input_text, context)
            specialist_outputs.append(out)
            return RunResult(
                final_output=json.dumps(out, indent=2, default=str),
                agent_history=agent_history,
                specialist_outputs=specialist_outputs,
                evidence=out.get("evidence", [])
            )

        elif agent.name.lower().startswith("pest"):
            from app.agents.pest_doctor import run_pest_doctor_agent
            out = run_pest_doctor_agent(input_text, context)
            specialist_outputs.append(out)
            return RunResult(
                final_output=json.dumps(out, indent=2, default=str),
                agent_history=agent_history,
                specialist_outputs=specialist_outputs,
                evidence=out.get("evidence", [])
            )

        elif agent.name.lower().startswith("market"):
            from app.agents.market import run_market_agent
            out = run_market_agent(input_text, context)
            specialist_outputs.append(out)
            return RunResult(
                final_output=json.dumps(out, indent=2, default=str),
                agent_history=agent_history,
                specialist_outputs=specialist_outputs,
                evidence=out.get("evidence", [])
            )

        elif agent.name.lower().startswith("finance"):
            from app.agents.finance_govt import run_finance_govt_agent
            out = run_finance_govt_agent(input_text, context)
            specialist_outputs.append(out)
            return RunResult(
                final_output=json.dumps(out, indent=2, default=str),
                agent_history=agent_history,
                specialist_outputs=specialist_outputs,
                evidence=out.get("evidence", [])
            )

        elif agent.name.lower().startswith("synthesis"):
            from app.agents.synthesis import run_synthesis_agent
            synthesis_res = run_synthesis_agent(
                query_text=input_text,
                specialist_outputs=specialist_outputs,
                farmer_profile=context.get("farmer_profile")
            )
            return RunResult(
                final_output=synthesis_res["markdown"],
                agent_history=agent_history,
                specialist_outputs=specialist_outputs,
                decision=synthesis_res.get("decision"),
                receipt=synthesis_res.get("receipt"),
                conflicts=synthesis_res.get("conflicts", []),
                evidence=synthesis_res.get("evidence", [])
            )

        else:
            return RunResult(
                final_output=f"Executed {agent.name}",
                agent_history=agent_history,
                specialist_outputs=specialist_outputs
            )
