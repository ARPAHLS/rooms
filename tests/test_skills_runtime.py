import types

from rooms.agent import Agent
from rooms.config import AgentConfig
from rooms.skills_runtime import SkillRuntime


def _build_fake_skill_module():
    module = types.ModuleType("fake_skill_module")

    class FakeSkill:
        __module__ = "fake_skill_module"

        def __init__(self, config=None):
            self.config = config or {}

        def execute(self, params):
            return {"echo": params, "cfg": self.config}

    module.FakeSkill = FakeSkill
    return module


def _build_fake_loader_module():
    module = _build_fake_skill_module()

    class FakeLoader:
        @staticmethod
        def load_skill(skill_id):
            return {
                "module": module,
                "manifest": {"name": skill_id},
                "instructions": "Use tool carefully.",
                "card": {},
            }

        @staticmethod
        def to_openai_tool(bundle):
            skill_id = bundle["manifest"]["name"]
            return {
                "type": "function",
                "function": {
                    "name": skill_id.replace("/", "_"),
                    "description": "fake tool",
                    "parameters": {
                        "type": "object",
                        "properties": {"q": {"type": "string"}},
                    },
                },
            }

    return types.SimpleNamespace(SkillLoader=FakeLoader)


def test_runtime_lazy_loading_skips_import_when_no_skills(monkeypatch):
    cfg = AgentConfig(name="A", system_prompt="S", skills=[])
    runtime = SkillRuntime(cfg)

    def _should_not_import(_name):
        raise AssertionError("Skillware import should not run")

    monkeypatch.setattr("rooms.skills_runtime.importlib.import_module", _should_not_import)
    assert runtime.get_tools() == []
    assert runtime.get_combined_instructions() == ""


def test_runtime_reports_missing_skillware(monkeypatch):
    cfg = AgentConfig(name="A", system_prompt="S", skills=["compliance/tos_evaluator"])
    runtime = SkillRuntime(cfg)

    def _missing(_name):
        raise ModuleNotFoundError("skillware unavailable")

    monkeypatch.setattr("rooms.skills_runtime.importlib.import_module", _missing)
    assert runtime.get_tools() == []
    assert runtime.load_error is not None
    assert "Install with: pip install skillware" in runtime.load_error


def test_runtime_enforces_session_call_limit(monkeypatch):
    cfg = AgentConfig(
        name="A",
        system_prompt="S",
        skills=["compliance/tos_evaluator"],
        max_skill_calls_per_session=0,
    )
    runtime = SkillRuntime(cfg)
    monkeypatch.setattr("rooms.skills_runtime.importlib.import_module", lambda _name: _build_fake_loader_module())
    runtime.get_tools()
    result = runtime.execute_tool("compliance_tos_evaluator", {"q": "hello"}, timeout_s=5)
    assert result["ok"] is False
    assert "Max skill calls per session reached" in result["error"]


def test_agent_executes_tool_and_returns_synthesized_reply(monkeypatch):
    calls = []
    monkeypatch.setattr("rooms.skills_runtime.importlib.import_module", lambda _name: _build_fake_loader_module())

    class _Function:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments

    class _ToolCall:
        def __init__(self, tc_id, name, arguments):
            self.id = tc_id
            self.function = _Function(name, arguments)

    class _Message:
        def __init__(self, content, tool_calls=None):
            self.content = content
            self.tool_calls = tool_calls or []

    class _Choice:
        def __init__(self, message):
            self.message = message

    class _Response:
        def __init__(self, message):
            self.choices = [_Choice(message)]

    def _fake_completion(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return _Response(
                _Message(
                    "",
                    tool_calls=[_ToolCall("call_1", "compliance_tos_evaluator", '{"q":"risk"}')],
                )
            )
        return _Response(_Message("Readable final answer"))

    monkeypatch.setattr("rooms.agent.litellm.completion", _fake_completion)
    agent = Agent(
        AgentConfig(
            name="A",
            system_prompt="S",
            skills=["compliance/tos_evaluator"],
            skill_settings={"compliance/tos_evaluator": {"mode": "strict"}},
        )
    )

    result = agent.generate_response(context_messages=[])
    assert result == "Readable final answer"
    assert len(calls) == 2
    assert "tools" in calls[0]
    second_messages = calls[1]["messages"]
    assert any(m.get("role") == "tool" for m in second_messages)


def test_wallet_screening_skill_flow_returns_natural_language(monkeypatch):
    """Simulate a flagged wallet check and ensure final output is natural language."""
    bad_wallet = "0x1111111111111111111111111111111111111111"
    tool_name = "finance_wallet_screening"
    calls = []

    module = types.ModuleType("wallet_skill_module")

    class WalletScreeningSkill:
        __module__ = "wallet_skill_module"

        def __init__(self, config=None):
            self.config = config or {}

        def execute(self, params):
            wallet = params.get("wallet", "")
            return {
                "wallet": wallet,
                "risk_level": "high",
                "flagged": wallet == bad_wallet,
                "reason": "Listed in sanctions dataset",
            }

    module.WalletScreeningSkill = WalletScreeningSkill

    class FakeLoader:
        @staticmethod
        def load_skill(skill_id):
            return {
                "module": module,
                "manifest": {"name": skill_id},
                "instructions": "Use this tool to screen wallets for risk flags.",
                "card": {},
            }

        @staticmethod
        def to_openai_tool(bundle):
            return {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": "Screen a wallet for risk",
                    "parameters": {
                        "type": "object",
                        "properties": {"wallet": {"type": "string"}},
                        "required": ["wallet"],
                    },
                },
            }

    monkeypatch.setattr("rooms.skills_runtime.importlib.import_module", lambda _name: types.SimpleNamespace(SkillLoader=FakeLoader))

    class _Function:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments

    class _ToolCall:
        def __init__(self, tc_id, name, arguments):
            self.id = tc_id
            self.function = _Function(name, arguments)

    class _Message:
        def __init__(self, content, tool_calls=None):
            self.content = content
            self.tool_calls = tool_calls or []

    class _Choice:
        def __init__(self, message):
            self.message = message

    class _Response:
        def __init__(self, message):
            self.choices = [_Choice(message)]

    def _fake_completion(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return _Response(
                _Message(
                    "",
                    tool_calls=[
                        _ToolCall(
                            "call_wallet",
                            tool_name,
                            '{"wallet":"0x1111111111111111111111111111111111111111"}',
                        )
                    ],
                )
            )
        return _Response(
            _Message(
                "I checked the wallet and it is high risk because it appears in a sanctions list."
            )
        )

    monkeypatch.setattr("rooms.agent.litellm.completion", _fake_completion)

    agent = Agent(
        AgentConfig(
            name="RiskAnalyst",
            system_prompt="Screen wallets and explain risk clearly.",
            model="ollama/gemma4:e2b",
            skills=["finance/wallet_screening"],
        )
    )

    reply = agent.generate_response([{"role": "user", "content": f"Check wallet {bad_wallet}"}])
    assert "high risk" in reply.lower()
    assert "{" not in reply and "}" not in reply
    assert len(calls) == 2
    tool_msgs = [m for m in calls[1]["messages"] if m.get("role") == "tool"]
    assert len(tool_msgs) == 1
    assert '"flagged": true' in tool_msgs[0]["content"].lower()
