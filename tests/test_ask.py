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


def test_interactive_mode_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    chat = FakeChat()
    questions = iter(["最初の質問", "続けて質問", "exit"])
    monkeypatch.setattr(ask_module, "create_chat", lambda: chat)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(questions))
    monkeypatch.setattr("sys.argv", ["app.ask", "--interactive"])

    ask_module.main()

    assert chat.questions == ["最初の質問", "続けて質問"]
    assert capsys.readouterr().out.count("回答") == 2