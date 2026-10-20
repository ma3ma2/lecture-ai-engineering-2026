"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask --interactive  # 会話履歴を保って続けて質問する
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールを使わない「素の」LLM呼び出し。通常モードでは会話履歴を持たず、
対話モードでは実行中のChatセッションに会話履歴を保持する。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def create_chat():
    client = genai.Client(api_key=get_api_key())
    return client.chats.create(model=MODEL)


def ask(chat, question: str) -> str:
    response = chat.send_message(question)

    usage = response.usage_metadata
    if usage is not None:
        print(
            f"[トークン数] 入力: {usage.prompt_token_count}, "
            f"出力: {usage.candidates_token_count}"
        )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--interactive", action="store_true", help="会話履歴を保って続けて質問する")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        chat = create_chat()
        if args.interactive:
            if args.question:
                print(f"[質問] {args.question}\n")
                print(ask(chat, args.question))
            while True:
                try:
                    question = input("\n質問（終了するには exit）> ").strip()
                except EOFError:
                    break
                if question.lower() in {"exit", "quit"}:
                    break
                if question:
                    print(ask(chat, question))
        else:
            question = args.question or DEFAULT_QUESTION
            print(f"[質問] {question}\n")
            print(ask(chat, question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
