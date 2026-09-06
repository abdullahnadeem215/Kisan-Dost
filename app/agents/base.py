"""
Core OpenAI Agents SDK primitives and provider-agnostic Runner for Kisan Dost.
Defines Agent, Runner, function_tool, Handoff, and RunResult objects.
Powered by Groq LLM API client (using GROQ_API_KEY) with OpenAI-compatible tool schemas.
"""
import os
import json
import inspect
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


def function_to_tool_schema(fn: Callable, custom_name: Optional[str] = None, custom_doc: Optional[str] = None) -> Dict[str, Any]:
    """
    Transforms a Python callable into an OpenAI-compatible function-calling tool schema.
    """
    name = custom_name or getattr(fn, "__name__", "custom_tool")
    raw_doc = custom_doc or inspect.getdoc(fn) or name
    description = raw_doc.strip().split("\n")[0]

    properties: Dict[str, Any] = {}
    required: List[str] = []

    try:
        sig = inspect.signature(fn)
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation in (dict, Dict):
                param_type = "object"
            elif param.annotation in (list, List):
                param_type = "array"

            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)
    except Exception as e:
        logger.debug(f"Could not inspect signature for {name}: {e}")

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }


class FunctionTool:
    """
    Wrapper around python functions for agent execution with OpenAI-compatible schema export.
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

    def to_openai_tool(self) -> Dict[str, Any]:
        """Returns OpenAI-compatible tool definition for Groq / OpenAI tool calling."""
        return function_to_tool_schema(self.fn, self.name, self.description)


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
    Holds agent name, system instructions, function tools, handoffs, and Groq LLM model identifier.
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

    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """Returns OpenAI-compatible tool specifications for all agent tools."""
        return [t.to_openai_tool() for t in self.tools]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Executes tool by name with arguments."""
        tool = self.get_tool(tool_name)
        if not tool:
            logger.warning(f"Tool '{tool_name}' not registered on agent {self.name}")
            return None
        return tool(**arguments)


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
    and Groq LLM API model routing with deterministic grounding fallbacks.
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
        Uses Groq API client when configured, while guaranteeing deterministic tool grounding.
        """
        context = context or {}
        agent_history: List[str] = [agent.name]
        specialist_outputs: List[Dict[str, Any]] = context.get("specialist_outputs", [])

        groq = GroqClient()

        # Check if starting at Triage Agent or an Agent with handoffs
        if agent.name.lower().startswith("triage"):
            from app.agents.triage import analyze_intents
            from app.agents.agronomy import agronomy_agent, run_agronomy_agent
            from app.agents.pest_doctor import pest_doctor_agent, run_pest_doctor_agent
            from app.agents.market import market_agent, run_market_agent
            from app.agents.finance_govt import finance_govt_agent, run_finance_govt_agent
            from app.agents.synthesis import synthesis_agent, run_synthesis_agent

            # 1. Triage Intent Analysis (Powered by Groq if available)
            intents = []
            if groq.is_configured():
                try:
                    triage_prompt = (
                        "You are the Triage Agent in Kisan Dost OpenAI Agents SDK network.\n"
                        "Analyze this Pakistani farmer query and classify required specialist agents.\n"
                        "Possible intents: ['agronomy', 'pest', 'market', 'finance_govt'].\n"
                        "Return pure JSON format: {\"intents\": [\"agronomy\", ...]}"
                    )
                    resp = groq.generate_completion(triage_prompt, input_text, json_mode=True)
                    if resp.get("success") and isinstance(resp.get("content"), dict):
                        intents = resp["content"].get("intents", [])
                except Exception as e:
                    logger.warning(f"Groq triage routing fallback: {e}")

            if not intents:
                intents = analyze_intents(input_text)

            logger.info(f"Triage agent routed intents: {intents}")

            # 2. Specialist Handoffs
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

            # 3. Perform Handoff to Synthesis Agent
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
