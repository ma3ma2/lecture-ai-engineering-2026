from app import ask as ask_module


class FakeResponse:
    text = "回答"
    usage_metadata = None


class FakeChat:
    def __init__(self):
        self.questions = []

    def send_message(self, question):
        self.questions.append(question)
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_interactive_mode_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    client = FakeClient()
    chat = FakeChat()
    questions = iter(["最初の質問", "続けて質問", "exit"])
    monkeypatch.setattr(ask_module, "create_chat", lambda: (client, chat))
    monkeypatch.setattr("builtins.input", lambda _prompt: next(questions))
    monkeypatch.setattr("sys.argv", ["app.ask", "--interactive"])

    ask_module.main()

    assert chat.questions == ["最初の質問", "続けて質問"]
    assert client.closed
    assert capsys.readouterr().out.count("回答") == 2


def test_ask_prints_response_time(monkeypatch, capsys):
    timestamps = iter([10.0, 11.25])
    monkeypatch.setattr(ask_module.time, "perf_counter", lambda: next(timestamps))

    assert ask_module.ask(FakeChat(), "質問") == "回答"
    assert "[応答時間] 1.25秒" in capsys.readouterr().out