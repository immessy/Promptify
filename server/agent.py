import os
from pydantic import BaseModel, Field
from typing import List
import strands
from strands.models.ollama import OllamaModel
from strands.models.anthropic import AnthropicModel
from dotenv import load_dotenv

load_dotenv()

# Data Models
class ClassifyResult(BaseModel):
    tier: str = Field(description="'novice', 'intermediate', or 'production'")
    reason: str = Field(description="A short, specific, human-readable reason referencing the signals found")
    signals_detected: List[str] = Field(description="The specific signals detected from the idea")

class Document(BaseModel):
    id: str = Field(description="Document ID (e.g., 'prompt', 'prd', 'tdd', 'grounding')")
    title: str = Field(description="Human readable title")
    content: str = Field(description="The generated markdown content for this document")

class GenerateResult(BaseModel):
    tier: str = Field(description="The confirmed tier this was generated for")
    documents: List[Document] = Field(description="The list of generated documents")

# Configure Model
# The user recommended anthropic for reliability or ollama for local. 
# We default to anthropic if ANTHROPIC_API_KEY is provided, else fallback to ollama.
if os.getenv("ANTHROPIC_API_KEY"):
    model = AnthropicModel()
else:
    model = OllamaModel(host="http://localhost:11434", model_id="llama3.1")

# System Prompts
CLASSIFICATION_SYSTEM_PROMPT = """
You are a task classification agent for an AI coding assistant.
Evaluate the raw user idea and suggest one of three tiers: novice, intermediate, or production.
Also provide a short, specific reason, and explicitly name the signals you detected.

Weigh the following signals:
- Scope/vision stated vs. implied — one-off vs. something the user intends to grow, maintain, or hand off.
- Integration surface — touches multiple services/external APIs vs. self-contained.
- Sensitive domains — auth, payments, personal/medical/financial data. Strong pull toward Production regardless of other signals.
- Persistence/state — needs a database/durable storage vs. stateless input->output.
- Audience — just the user vs. other people/customers/public.
- Ambiguity in the raw idea — well-defined vs. vague. Vague pushes the tier *up*, since that's when an unguided agent is most likely to drift.
- Explicit scale language — "just for me," "quick," "prototype" vs. "scalable," "production," "many users."

Tier decision guidance:
- Any strong sensitive-domain or clear multi-user/production language -> production.
- Real shape (a few components, meant to be kept/iterated on) but single-user, no ops concerns -> intermediate.
- Small, self-contained, one-off -> novice.
- When signals conflict, ambiguity itself is a signal — default up a tier rather than down.
"""

NOVICE_GENERATION_PROMPT = """
Rewrite the raw idea into one well-structured prompt: clear goal, relevant constraints/context pulled out of the raw idea, and an explicit statement of expected output format. No other documents.
Return a single document with id="prompt" and title="Structured Prompt".
"""

INTERMEDIATE_GENERATION_PROMPT = """
Produce a lightweight PRD (what/why, goals, explicit out-of-scope) and a lightweight TDD (how, rough components/architecture, data flow). Keep both short — this tier should not feel like Production-lite, it should feel proportionate to a small, real task.
Return two documents:
1. id="prd", title="PRD"
2. id="tdd", title="Technical Design Doc"
"""

PRODUCTION_GENERATION_PROMPT = """
Everything Intermediate produces, plus: hosting/deploy requirements, auth model, data/storage decisions, security and error-handling expectations, all structured under spec-driven development principles (the spec is the source of truth, not a one-time doc). 
Additionally produce a grounding document (id="grounding", title="CLAUDE.md (Agent Grounding)") whose job is to instruct whatever agent receives it to check its own progress against the spec at every major milestone before continuing. (Do not enforce or monitor that loop — just bake the instruction into the doc).
Return four documents:
1. id="prompt", title="Structured Prompt"
2. id="prd", title="PRD"
3. id="tdd", title="Technical Design Doc"
4. id="grounding", title="CLAUDE.md (Agent Grounding)"
"""

classifier_agent = strands.Agent(
    model=model,
    system_prompt=CLASSIFICATION_SYSTEM_PROMPT
)

def get_generation_agent(tier: str) -> strands.Agent:
    if tier == "novice":
        system_prompt = NOVICE_GENERATION_PROMPT
    elif tier == "intermediate":
        system_prompt = INTERMEDIATE_GENERATION_PROMPT
    elif tier == "production":
        system_prompt = PRODUCTION_GENERATION_PROMPT
    else:
        raise ValueError(f"Unknown tier: {tier}")
        
    return strands.Agent(
        model=model,
        system_prompt=system_prompt
    )

def classify_idea(idea: str) -> ClassifyResult:
    result = classifier_agent.structured_output(ClassifyResult, prompt=idea)
    return result

def generate_documents(idea: str, tier: str) -> GenerateResult:
    agent = get_generation_agent(tier)
    result = agent.structured_output(GenerateResult, prompt=f"Raw idea: {idea}")
    result.tier = tier # enforce the tier matches the request
    return result
