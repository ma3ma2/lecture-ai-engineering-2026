"""第3回 宿題（実装）: save_learning_log と、保存前の承認のテスト（LLMもAPIキーも使わない）。"""

import pytest
from pydantic_ai import DeferredToolRequests, DeferredToolResults, ToolDenied
from pydantic_ai.models.test import TestModel

from app import tools
from app.agent import agent, run_with_approval


@pytest.fixture
def log_dir(tmp_path, monkeypatch):
    """本物の learning_log/ を汚さないよう、保存先を一時フォルダに差し替える。"""
    path = tmp_path / "learning_log"
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", path)
    return path


def test_save_learning_log_writes_markdown(log_dir):
    message = tools.save_learning_log("LoRAとQLoRA", "QLoRAは量子化したモデルにLoRAを使う。")
    files = list(log_dir.glob("*.md"))
    assert len(files) == 1 and files[0].name in message
    text = files[0].read_text(encoding="utf-8")
    assert text.startswith("# LoRAとQLoRA") and "量子化" in text


def test_save_learning_log_does_not_overwrite(log_dir):
    tools.save_learning_log("1回目", "a")
    tools.save_learning_log("2回目", "b")
    assert len(list(log_dir.glob("*.md"))) == 2


def test_save_learning_log_rejects_empty(log_dir):
    assert "保存していません" in tools.save_learning_log(" ", "本文")
    assert not log_dir.exists()


def _run_until_approval():
    result = agent.run_sync("学習の記録を保存して", model=TestModel(call_tools=["save_learning_log"]))
    assert isinstance(result.output, DeferredToolRequests)
    [call] = result.output.approvals
    assert call.tool_name == "save_learning_log"
    return result, call


def test_save_waits_for_approval_and_saves_when_approved(log_dir):
    result, call = _run_until_approval()
    assert not log_dir.exists()  # 承認されるまでは保存しない

    result = agent.run_sync(
        message_history=result.all_messages(),
        deferred_tool_results=DeferredToolResults(approvals={call.tool_call_id: True}),
        model=TestModel(call_tools=[]),
    )
    assert isinstance(result.output, str)
    assert len(list(log_dir.glob("*.md"))) == 1


def test_save_is_skipped_when_denied(log_dir):
    result, call = _run_until_approval()
    result = agent.run_sync(
        message_history=result.all_messages(),
        deferred_tool_results=DeferredToolResults(
            approvals={call.tool_call_id: ToolDenied("利用者が実行を許可しませんでした。")}
        ),
        model=TestModel(call_tools=[]),
    )
    assert isinstance(result.output, str)
    assert not log_dir.exists()


@pytest.mark.parametrize("answer, saved", [("y", 1), ("n", 0), ("", 0)])
def test_cli_asks_before_saving(log_dir, monkeypatch, answer, saved):
    monkeypatch.setattr("builtins.input", lambda _prompt: answer)
    result = run_with_approval(agent, "学習の記録を保存して", TestModel(call_tools=["save_learning_log"]))
    assert isinstance(result.output, str)
    assert len(list(log_dir.glob("*.md"))) == saved
