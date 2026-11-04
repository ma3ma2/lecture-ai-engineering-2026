"""第3回 宿題（発展 a）: 演習のエージェントを Google ADK で組み立て直す。

指示（INSTRUCTIONS）とツールは app/ のものをそのまま使い、組み立てる部分だけを書き直す。

動かす（リポジトリの直下で）:
    PYTHONPATH=. uv run --with google-adk adk run adk_agent/glossary_agent
"""

from google.adk.agents import Agent

from app import tools
from app.agent import INSTRUCTIONS
from app.config import MODEL

root_agent = Agent(
    model=MODEL,  # 演習と同じモデル（既定は gemini-3.5-flash-lite。AIE_MODEL で切り替え）
    name="glossary_agent",
    # 演習と同じ指示。ただし、ここでは渡さない save_learning_log に触れた行だけ除く
    # （残すと、モデルが存在しないツールを呼ぼうとしてエラーになることがあるため）
    instruction="\n".join(
        line for line in INSTRUCTIONS.splitlines() if "save_learning_log" not in line
    ),
    # 関数をそのまま渡すと、docstring と型ヒントがツールの説明になる（Pydantic AI と同じ）。
    # 承認付きのツール（save_learning_log）は対象外なので渡さない。
    tools=[tools.search_glossary, tools.get_lecture_summary],
)
