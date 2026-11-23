"""第6回: 用語集と各回の要点を MCP サーバーとして公開する。

使い方:
    uv run python -m app.mcp_agent --list-tools     # このサーバーが公開するツールを一覧する（APIキー不要）
    uv run python -m app.mcp_server --http          # Streamable HTTP で起動する（http://127.0.0.1:8000/mcp）

引数なしで実行すると stdio（標準入出力）で待ち受ける。これは MCP クライアント（app.mcp_agent など）が
サブプロセスとして起動する使い方なので、手で実行すると入力待ちのまま止まって見える。

第3回では tools.py の関数を agent.py に直接登録した。MCP サーバーにすると、同じ関数を
エージェントのプログラム（app/mcp_agent.py）からも、MCP に対応したほかのソフトウェアからも、
共通の手順で使えるようになる。
"""

import argparse

from mcp.server.mcpserver import MCPServer

from app import tools

# サーバーの名前と説明。クライアントに表示される（設定ファイル側のキー "glossary" とは別物）
server = MCPServer(
    "aie2026-glossary",
    instructions="AIE2026（AIエンジニアリング実践講座）の用語集と各回の要点を提供する。",
)

# 第3回と同じ関数を、そのまま MCP のツールとして公開する。docstring と型ヒントが説明文になる
server.tool()(tools.search_glossary)

# TODO(宿題・基礎): get_lecture_summary も公開しよう
server.tool()(tools.get_lecture_summary)


@server.tool()
def make_quiz(lecture: int) -> str:
    """指定した回の講義内容からクイズを1問作る。

    「第2回のクイズを作って」のように頼まれたときに使う。
    lecture には回の番号を指定する。
    """
    path = tools.DATA_DIR / "lectures" / f"{lecture:02d}.md"
    if not path.exists():
        available = ", ".join(
            sorted(p.stem for p in (tools.DATA_DIR / "lectures").glob("*.md"))
        )
        return f"第{lecture}回の講義資料はありません。クイズを作れる回: {available}"

    text = path.read_text(encoding="utf-8")
    goals = text.partition("## この回のねらい")[2].partition("\n## ")[0]
    first_goal = next(
        (line[2:].strip() for line in goals.splitlines() if line.startswith("- ")),
        None,
    )
    if first_goal is None:
        return f"第{lecture}回の講義資料から、クイズに使う内容を見つけられませんでした。"

    return (
        f"問題：第{lecture}回で学ぶ内容を1つ答えてください。\n"
        f"解答例：{first_goal}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="用語集 MCP サーバー")
    parser.add_argument("--http", action="store_true", help="Streamable HTTP で起動する（既定は stdio）")
    args = parser.parse_args()
    if args.http:
        print("MCP サーバーを http://127.0.0.1:8000/mcp で起動します（Ctrl+C で停止）")
        server.run(transport="streamable-http")
    else:
        # stdio では標準出力がプロトコルの通信路になるので、print してはいけない
        server.run()


if __name__ == "__main__":
    main()
