# 第6回 解答

## 演習

- STEP 1 のツールの名前：`search_materials`（従来のエージェント）、`glossary_search_glossary`（MCP エージェント）
- STEP 2 の [tool call]：`glossary_search_glossary({'query': '3レベル'})`
- STEP 3 の [tool call]：`fetch_fetch({'url': 'https://modelcontextprotocol.io/'})`
- STEP 4 の [tool call]：
  - `aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'Amazon S3 バージョニング 概要'})`
  - `aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'Using versioning in S3 buckets'})`
- 気づき・疑問：`--list-tools` で、用語集・fetch・AWS のサーバーを追加するたびに、モデルに見えるツールが増えることを確認した。`--trace` では、STEP 2～4 のツール呼び出しと引数を確認できた。

## 宿題

- 取り組んだレベル：基礎
- やったこと：`app/mcp_server.py` で `get_lecture_summary` を MCP ツールとして公開した。エージェント側のコードを変更せずに `--list-tools` と `--trace "第2回では何を学びますか？"` を実行し、最後に `uv run pytest -q` でテストした。
- 結果：ツール一覧に `glossary_get_lecture_summary` が増え、モデルに見えるツールは計8個になった。質問時には `[tool call] glossary_get_lecture_summary({'lecture': 2})` が表示され、第2回の講義内容を取得して回答した。テストは `21 passed` だった。
- 気づき・疑問：サーバー側で公開するツールを追加すると、エージェント側の設定やコードを変更しなくても、新しいツールを認識して使えた。

