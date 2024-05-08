import pytest
from persona_rag.agents import Agent

def test_agent_initialization():
    agent = Agent(template="Hello {name}", model="gpt-4")
    assert agent.model == "gpt-4"