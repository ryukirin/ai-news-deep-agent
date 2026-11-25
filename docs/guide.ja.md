# ai-news-deep-agent 詳細ガイド

[English](guide.md) | 日本語 | [中文](guide.zh-CN.md)

プロジェクトの概要は [README](../README.ja.md) を参照。

[Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) で構築した AI ニュースアシスタント。メインエージェントが、ニュース収集、重複排除、過去ニュースとの照合、レポート作成の 4 ステップを 4 つのサブエージェントに順に委任する。レポート作成後、メインエージェントは `append_history` を呼び出し、レポートで使ったニュースを履歴に追記する。重複排除と過去ニュース照合のルールは `skills/` 配下の Skill に定義している。ニュースの検索には Tavily を使う。履歴、レポート、長期記憶はユーザーごとに SQLite に保存する。

中国のオープンソース学習コミュニティ Datawhale が公開している中国語の講座 [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action)（Deep Agents 実践）の学習用プロジェクト。

## 学習の進捗

| 章 | 状態 |
| --- | --- |
| 第 1 章 [Agent Framework から Agent Harness へ](https://datawhalechina.github.io/deepagents-in-action/chapters/ch01-agent-harness/) | 完了 |
| 第 2 章 [クイックスタート](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/) | 完了 |
| 第 3 章 [仮想ファイルシステム](https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/) | 完了 |
| 第 4 章 [タスクの計画と分解](https://datawhalechina.github.io/deepagents-in-action/chapters/ch04-task-planning/) | 完了 |
| 第 5 章 [サブエージェントとコンテキストの分離](https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/) | 完了 |
| 第 6 章 [非同期サブエージェント](https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/) | スキップ（選択課題） |
| 第 7 章 [Skills](https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/) | 完了 |
| 第 8 章 [長期記憶](https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/) | 完了 |
| 第 9 章 [Human-in-the-Loop](https://datawhalechina.github.io/deepagents-in-action/chapters/ch09-human-in-the-loop/) | 完了 |
| 第 10 章から第 16 章 | スキップ |

2026-11-02 時点の進捗。

## 講座との対応

`agent.py` と `tool.py` は第 2 章のリサーチアシスタントの例をもとにしている。ストレージバックエンドは第 3 章、サブエージェントは第 5 章、Skill は第 7 章、長期記憶とユーザーごとのストレージ分割は第 8 章、人間による承認は第 9 章に沿って実装した。第 2 章の内容と本プロジェクトの対応:

| 講座の内容 | 本プロジェクト |
| --- | --- |
| `ChatOpenAI` と `base_url` で OpenAI 互換モデルに接続 | `agent.py` |
| カスタムツール（引数の型注釈、戻り値の型、docstring） | `tool.py` の `internet_search` |
| `TodoListMiddleware` を明示的に追加し、`write_todos` によるタスク計画を有効化 | `agent.py` |
| LangSmith によるトレース | `.env.example` の `LANGSMITH_*` 変数 |

第 3 章の内容と本プロジェクトの対応:

| 講座の内容 | 本プロジェクト |
| --- | --- |
| `CompositeBackend` によるパスプレフィックス単位のルーティング | `agent.py` |
| デフォルトバックエンドとしての `StateBackend` | `agent.py` |
| セッションをまたいで永続化する `StoreBackend` | `agent.py` の `/history/`、`/report/`、`/memories/` ルート |
| ローカルディスクを読み書きする `FilesystemBackend` | `agent.py` の `/skills/` ルート |

第 5 章の内容と本プロジェクトの対応:

| 講座の内容 | 本プロジェクト |
| --- | --- |
| 辞書形式でのサブエージェント定義 | `agent.py` の `subagents`（4 つ） |
| 複数サブエージェントの連携 | `config.py` の `USER_PROMPT` が 4 つのサブエージェントに順に委任 |
| 構造化出力（`response_format`） | `news_model.py` の `NewsList`。`news-collector`、`news-categorizer`、`old-news-checker` で使用 |
| サブエージェントごとに異なるモデル | `response_format` を持つ 3 つのサブエージェントは `agent.py` の `structured_model` を使用 |

第 7 章の内容と本プロジェクトの対応:

| 講座の内容 | 本プロジェクト |
| --- | --- |
| SKILL.md の構成（frontmatter の `name`、`description` と本文） | `skills/news-categorizer/news-dedup/SKILL.md`、`skills/old-news-checker/history-check/SKILL.md` |
| `/skills/` を `FilesystemBackend` にルーティング | `agent.py` |
| サブエージェントの spec の `skills` で Skill の読み込み元ディレクトリを指定 | `agent.py`。読み込み元ディレクトリをサブエージェント名で分けており、`news-categorizer` は `news-dedup` だけ、`old-news-checker` は `history-check` だけを読み込む |
| 読み取り専用の Skill（`FilesystemPermission` で `/skills/**` への書き込みを拒否） | `agent.py` の `permissions`。サブエージェントは独自の `permissions` を持たず、このルールを継承する |

第 8 章の内容と本プロジェクトの対応:

| 講座の内容 | 本プロジェクト |
| --- | --- |
| `memory=` による記憶ファイルの読み込み | `agent.py` で `/memories/preferences.md` を読み込む |
| `context_schema` による実行時の ID の受け渡し | `memory_model.py` の `MemoryContext`。`user_id` のデフォルトは `local-user` |
| namespace 関数によるユーザーごとのデータ分離 | `identity.py` の `user_namespace`。`/history/`、`/report/`、`/memories/` の namespace はそれぞれ `(ユーザー, "history")`、`(ユーザー, "report")`、`(ユーザー, "memories")` |

第 9 章の内容と本プロジェクトの対応:

| 講座の内容 | 本プロジェクト |
| --- | --- |
| `interrupt_on` と `when` で一部の呼び出しだけを中断 | `agent.py` の `protected_path`。`write_file`、`edit_file`、`delete` の対象が `/history/` または `/report/` 配下のときに中断する |
| `allowed_decisions` で選べる判断を制限 | `approve` と `reject` のみ |
| Checkpointer と `thread_id` | `MemorySaver`。実行ごとに新しい `thread_id` を生成 |
| `Command(resume=...)` による再開 | `agent.py` 末尾のループ。判断は `ask_user.py` の `ask_decision` がコマンドラインから読み取る |

人間による承認は第 9 章の演習としてのみ実装している。ai-news が書き込むのは履歴とレポートだけで承認は不要なため、`agent.py` の `interrupt_on` はコメントアウトしてあり、実行は一時停止しない。コメントを外すと承認が再び有効になる。`protected_path`、再開ループ、`ask_user.py` は残してある。

講座の例から変更した点:

- 検索のトピックをニュース（`topic="news"`）に固定。期間はデフォルトで直近 1 日（`time_range="day"`）とし、モデルが `week` か `month` に広げられる。検索のエラーは `{"error": ..., "results": []}` としてモデルに返し、実行は止めない。
- `NewsArticle` に `url` と `published_date` を追加し、検索結果からコピーする。`report-generator` は各記事に `url` へのリンクを付け、`append_history` の各行は `published_date` を日付に使う。
- `get_current_time` ツールを追加。モデルが現在の日時を取得できる。
- `append_history` ツールを追加。レポートで使ったニュースを `/history/news_history.txt` に追記する。各行は `YYYY-MM-DD | タイトル | 要約` の形式でなければならず、1 行でも合わなければ全件を書き込まずにフォーマットエラーを返す。既存の行と完全に一致する行はスキップする。ツールは `ToolRuntime` の `store` から直接 Store に書き込み、`write_file` を経由しない。
- `permissions` で `/history/**` への書き込みも拒否し、サブエージェントもこのルールを継承する。`write_file`、`edit_file`、`delete` で履歴を操作すると permission denied が返るため、履歴は `append_history` でしか追記できない。
- 環境変数、システムプロンプト（`SYSTEM_PROMPT`）、ユーザープロンプト（`USER_PROMPT`）を `config.py` にまとめた。`.env` は `python-dotenv` で読み込む。
- `StoreBackend` には講座の例の `InMemoryStore` の代わりに `SqliteStore`（`news.db`）を使い、履歴を実行間で保持する。
- `structured_model` は `extra_body={"thinking": {"type": "disabled"}}` で DeepSeek の思考モードをオフにしている。思考モードでは、構造化出力が使う `tool_choice` が 400 を返す。
- `news-collector` に `ToolCallLimitMiddleware` を追加し、1 回の委任で `internet_search` を呼べる回数を 10 回までにした。

## 前提条件

- Python 3.11 以上（deepagents 0.7.25 の要件）。動作確認は Python 3.12 で実施。
- ツール呼び出しに対応した OpenAI 互換のモデルサービスとその API キー。
- [Tavily](https://tavily.com) の API キー。
- LangSmith の API キー（任意。トレースに使う）。
- `agentseek dev` には AgentSeek CLI（`uv tool install agentseek`）と uv も必要で、どちらも `PATH` に含まれている必要がある。動作確認したバージョンは agentseek 0.1.6、uv 0.13.0。

## インストール

```bash
git clone https://github.com/ryukirin/ai-news-deep-agent.git
cd ai-news-deep-agent
python -m venv .venv
```

仮想環境を有効にする。

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

依存パッケージをインストールする。

```bash
pip install -r requirements.txt
```

`requirements.txt` は `requirements.in` から生成し、すべての依存パッケージのバージョンを固定している。主なものは deepagents 0.7.25、langchain 1.4.6、langchain-openai 1.7.2、langgraph 1.2.15、langgraph-checkpoint-sqlite 3.1.2、tavily-python 0.8.5、langgraph-cli 0.4.40、langgraph-api 0.17.0、langgraph-runtime-inmem 0.37.0。

依存パッケージを更新するときは `requirements.in` を編集し、再生成する。

```bash
uv pip compile requirements.in --universal --python-version 3.11 --no-annotate -o requirements.txt
```

## 設定

`.env.example` を `.env` にコピーし、次の変数を設定する。

| 変数 | 説明 |
| --- | --- |
| `MODEL_NAME` | モデル名 |
| `DEEPSEEK_API_KEY` | モデルサービスの API キー。他の OpenAI 互換サービスでもこの変数を使う |
| `BASE_URL` | OpenAI 互換 API のベース URL |
| `TAVILY_API_KEY` | Tavily の API キー |
| `LANGSMITH_TRACING` | LangSmith のトレースを有効にするか。`.env.example` では `true` |
| `LANGSMITH_API_KEY` | LangSmith の API キー |
| `LANGSMITH_PROJECT` | LangSmith のプロジェクト名 |
| `LANGSMITH_ENDPOINT` | LangSmith のトレース API のエンドポイント。`.env.example` は APAC リージョン。他のリージョンのエンドポイントは講座の第 2 章を参照 |

最初の 4 つの変数のどれかが欠けていると、起動時に変数名を含む `KeyError` が発生する。LangSmith を使わない場合は `LANGSMITH_TRACING` を `false` にする。

## 使い方

```bash
python agent.py
```

プロジェクトのルートで実行する。プロンプトは `config.py` の `USER_PROMPT` で、手順は次のとおり。

1. `news-collector` に委任し、ニュースを 10 件収集する。
2. `news-categorizer` に委任し、重複を取り除く。
3. `old-news-checker` に委任し、`/history/news_history.txt` の過去ニュースと照合して、過去のニュースを取り除く。
4. `report-generator` に委任し、当日の日付をファイル名にしたレポートを `/report/` に書き込む。
5. `append_history` を呼び出し、レポートで使ったニュースを `/history/news_history.txt` に追記する。

実行は一時停止しない。`interrupt_on` を再び有効にすると、`write_file`、`edit_file`、`delete` の対象が `/history/` または `/report/` 配下のときに実行が一時停止し、ターミナルにツール名、引数、選べる判断が表示される。

```text
Tool: write_file
Args: {"file_path": "/report/2026-10-29.md", "content": "..."}
Allowed decisions: approve, reject
Enter a decision:
```

`approve` を入力するとその呼び出しを実行する。`reject` を入力すると呼び出しを取り消し、続けて拒否の理由の入力を求める（空欄可）。理由はモデルに返される。それ以外を入力すると再入力を求める。サブエージェント内の呼び出しでも同様に一時停止する。他のパス（`/memories/` を含む）への書き込みでは一時停止しない。

`/history/` への書き込みは拒否される。`write_file`、`edit_file`、`delete` の対象が `/history/` の場合も一時停止はし、承認後に permission denied が返る。`append_history` は `interrupt_on` に含まれず、呼び出しても一時停止しない。

サブエージェントの設定:

| サブエージェント | システムプロンプト | Skill | 戻り値の形式 | モデル | 検索回数の上限 |
| --- | --- | --- | --- | --- | --- |
| `news-collector` | `NEWS_COLLECTOR_PROMPT` | なし | `NewsList` | `structured_model` | 10 |
| `news-categorizer` | `NEWS_CATEGORIZER_PROMPT` | `news-dedup` | `NewsList` | `structured_model` | なし |
| `old-news-checker` | `OLD_NEWS_CHECKER_PROMPT` | `history-check` | `NewsList` | `structured_model` | なし |
| `report-generator` | `REPORT_GENERATOR_PROMPT` | なし | テキスト | メインエージェントと同じ | なし |

サブエージェントの `tools` は `internet_search` と `get_current_time` を明示的に指定しており、`append_history` は含まない。

2026-10-24 の実行では 273 秒かかった。`news-categorizer` と `old-news-checker` はそれぞれ自分の SKILL.md を `read_file` で読み込んだ。重複排除で 10 件が 9 件にまとまり、過去ニュースとの照合で除外されたのは 0 件。`old-news-checker` が履歴に 9 件を書き込み（58 件から 67 件）、`report/2026-10-24.md` が生成された。

実行が終わると、ターミナルにエージェントの最終回答が表示される。

エージェントが使うパスと実際の保存先:

| エージェント内のパス | 保存先 |
| --- | --- |
| `/history/news_history.txt` | `news.db`（SQLite）の `store` テーブル、namespace は `(ユーザー, "history")` |
| `/report/<日付>.md` | `news.db` の `store` テーブル、namespace は `(ユーザー, "report")` |
| `/memories/` 配下のパス | `news.db` の `store` テーブル、namespace は `(ユーザー, "memories")` |
| `/skills/` 配下のパス | `skills/` ディレクトリ（読み取り専用） |
| その他のパス | エージェントの state。実行終了後は残らない |

ユーザーは `identity.py` の `user_namespace` で決まる。`rt.server_info.user` があればその `identity` を使い、なければ context の `user_id` を使う。`agent.py` は `invoke` で context を渡していないため、現在のユーザーは常に `local-user`。

履歴は 1 行 1 件で、形式は `日付 | タイトル | 要約`。日付は単一の `YYYY-MM-DD` で、書き込み時に `append_history` が検証する。

レポートは `report/` ディレクトリには書き込まない。特定の日のレポートは、プロジェクトのルートで次のコードを実行して読む。

```python
from langgraph.store.sqlite import SqliteStore

with SqliteStore.from_conn_string("news.db") as store:
    item = store.get(("local-user", "report"), "/2026-10-29.md")
    print(item.value["content"])
```

## バックエンドサーバーの起動

```bash
agentseek doctor
agentseek dev
```

プロジェクトのルートで実行する。`agentseek dev` は `.agentseek/lifecycle.toml` に従って `uv`、必須ファイル、`.env` の最初の 4 つの変数を確認したうえで、`uv run --no-project langgraph dev --no-browser --allow-blocking --port 2024` を実行する。`uv run` はプロジェクトのルートの `.venv` を使うため、仮想環境を有効にしなくてよい。サーバーはバックエンドのみで、フロントエンドはない。

| URL | 説明 |
| --- | --- |
| `http://127.0.0.1:2024` | LangGraph API。グラフ名は `ai-news`（`langgraph.json` を参照） |
| `http://127.0.0.1:2024/ok` | ヘルスチェック。`agentseek doctor --live` がこの URL にリクエストする |
| `http://127.0.0.1:2024/docs` | API ドキュメント |

依存パッケージが変わったときは `agentseek task sync` を実行する。`uv pip install -r requirements.txt` と同じ処理になる。

バックエンドサーバーと `python agent.py` の違い:

| 項目 | `python agent.py` | `agentseek dev` |
| --- | --- | --- |
| ユーザープロンプト | `config.py` の `USER_PROMPT` | クライアントがリクエストで渡す。`USER_PROMPT` は読まない |
| Store | `SqliteStore`（`news.db`） | `news_store.py` の `AsyncSqliteStore`（同じ `news.db`） |
| Checkpointer | `MemorySaver` | サーバー側が提供。データは `.langgraph_api/` |
| 人間による承認を再び有効にした場合 | `ask_user.py` がターミナルから判断を読み取る | クライアントが API で `Command(resume=...)` を送る |

認証なしの場合もユーザーは `local-user` になり、`python agent.py` が書き込んだ履歴、レポート、記憶を読める。

`--allow-blocking` は開発サーバーのブロッキング呼び出し検出をオフにする。deepagents の権限チェックは非同期ツールの中で `Path.resolve()` を同期的に呼ぶため、このオプションがないと `ls` で `BlockingError` が発生する。このオプションはローカル開発でのみ使う。

2026-11-02 に Windows 11、Python 3.12.10、deepagents 0.7.25 で確認した結果: `ls` は正常に結果を返し、`news-categorizer` は Skill を読み込んで重複する 2 件のニュースを 1 件にまとめた。`interrupt_on` を有効にした状態で 4 ステップのパイプライン全体が通り、20 件を収集、重複排除後 20 件、過去ニュースとの照合で 1 件を除外、履歴は 10 件から 29 件に増え、`/report/2026-11-02.md` が生成された。`interrupt_on` をコメントアウトすると、`/report/` への書き込みで一時停止しなくなった。

## 再現可能なデモ

デモでは、1 つのアプリケーションが 3 つの機能（サブエージェントへの委任、サブエージェントごとの Skill の読み込み、Store による履歴とレポートの永続化）を組み合わせて使えることを確認する。入力は `config.py` の `USER_PROMPT` に固定している。ニュースの内容は毎日変わるため、確認するのは処理の流れと書き込み結果だけ。

`news.db` が空の状態のクリーンなクローンで実行する。既存の `news.db` で実行すると、履歴は追記され続け、当日のレポートは上書きされる。

```powershell
git clone https://github.com/ryukirin/ai-news-deep-agent.git
cd ai-news-deep-agent
python -m venv .venv
agentseek task sync
Copy-Item .env.example .env
```

`.env` の最初の 4 つの変数を設定し、サーバーを起動する。

```powershell
agentseek doctor
agentseek dev
```

別のターミナルを開き、プロジェクトのルートで実行する。

```powershell
uv run --no-project python demo.py
```

`agentseek task sync` と `uv run` は `VIRTUAL_ENV` が指す環境を優先する。実行前に他の仮想環境を有効にしないこと。

`.venv` 内で最も長いファイル（anthropic 1.14.0 のもの）は、プロジェクトのルートからの相対パスが 132 文字ある。Windows でロングパスが無効（`LongPathsEnabled=0`）の場合、プロジェクトのルートのパスは 126 文字以内でなければならない。超えるとサーバー起動時に `ModuleNotFoundError: No module named 'anthropic.types.beta...'` が発生する。

`demo.py` は固定の入力を送り、実行の終了を待ってから次の項目を確認する。すべて合格なら終了コードは 0、それ以外は 1。

| 確認項目（出力上の名前） | 合格条件 |
| --- | --- |
| Run finished | スレッドの状態が `idle` で、エラーイベントがない |
| Subagents | メインエージェントが最初に委任した順序が `news-collector`、`news-categorizer`、`old-news-checker`、`report-generator` |
| Skills | 2 つの SKILL.md がどちらもサブエージェント内で `read_file` により読み込まれた |
| History | `news.db` に 1 件以上が追加され、各行が `日付 \| タイトル \| 要約` の形式 |
| History path | `/history/` 配下には `news_history.txt` しかない |
| Report | ファイル名に当日の日付を含む空でないレポートが `news.db` に書き込まれた |
| Report links | レポートに Markdown のリンク（`[...](http...)`）が 1 つ以上ある |

2026-11-26 に Windows 11、Python 3.12.10 で、空の `news.db` から実行した結果（所要時間 115 秒）:

```text
PASS  Run finished: thread status idle, 0 error events
PASS  Subagents: delegation order news-collector -> news-categorizer -> old-news-checker -> report-generator
PASS  Skills: both SKILL.md files read inside subagents
PASS  History: 11 lines added, 0 with invalid format
PASS  History path: files under /history/: ['/news_history.txt']
PASS  Report: written in this run: ['/2026-11-26.md']
PASS  Report links: 11 links to original articles

7/7 checks passed
```

レポートには 11 件の記事があり、すべてに元記事へのリンクと公開日が付いている。履歴の 11 行は記事の公開日（2026-11-24 と 2026-11-25）を使っている。レポートは [examples/2026-11-26.md](examples/2026-11-26.md) にある。

確認結果はモデルの出力に左右されるため、一部の項目が不合格になることがある。2026-11-02 の実行では、モデルが日付を `2026-10-30/31` と書いたため History が不合格になった。現在は `append_history` が日付の形式を検証し、形式に合わない行は書き込まない。

`demo_users.py` は同じサーバーで、ユーザーごとの名前空間を検証する。ユーザー `demo-alice` と `demo-bob` の `/memories/preferences.md` を削除してから、`context={"user_id": ...}` を付けてエージェントを 3 回実行し、次の項目を確認する。

| 確認項目（出力上の名前） | 合格条件 |
| --- | --- |
| Read isolation | `demo-alice` が書いたファイルを `demo-bob` が読めない |
| Namespace (demo-alice, memories)、Namespace (demo-bob, memories) | 各ユーザーの `/memories/preferences.md` にそのユーザーの行だけがある |
| Namespace (local-user, memories) | `local-user` のファイル一覧が変わっていない |

サーバーの起動中に、プロジェクトのルートで実行する。

```powershell
uv run --no-project python demo_users.py
```

2026-11-26 に `demo.py` の後で実行した結果（所要時間 34 秒）:

```text
PASS  Read isolation: demo-bob reads /memories/preferences.md after demo-alice wrote it, answer 'NONE'
PASS  Namespace (demo-alice, memories): /memories/preferences.md = 'Preferred topics: AI chips and data centers'
PASS  Namespace (demo-bob, memories): /memories/preferences.md = 'Preferred topics: AI regulation'
PASS  Namespace (local-user, memories): unchanged, files []

4/4 checks passed
```

## 既知の制限

- 同じ日に再実行すると `/report/<日付>.md` が上書きされ、以前の版は復元できない。
- 検索回数の上限があるのは `news-collector` だけ。メインエージェントと他のサブエージェントは `internet_search` を無制限に呼べる。
- 履歴への書き込みは、メインエージェントが `USER_PROMPT` の手順 5 に従って `append_history` を呼ぶことに依存している。呼ばれなければ書き込まれない。
- 履歴に出典のフィールドがない。要約にモデルの照合結果のメモが混ざることがある。
- メインエージェントには `skills` を設定していないが、`/skills/` ルートから SKILL.md を直接読める。2026-10-24 の実行では、メインエージェントが委任前に 2 つの SKILL.md を読んだ。
- 最終回答に含まれる件数はモデルの自己申告で、`news.db` と一致しないことがある。2026-10-24 の実行では履歴が「68 行」と報告されたが、`news.db` の空でない行は 67 行だった。
- プロンプトは `config.py` に固定で、コマンドライン引数に対応していない。
- 出力言語の設定はない。レポートと履歴はプロンプトの言語（英語）に従うが、記憶ファイルの内容で変わる。2026-11-26 に既存の `news.db` で 2 回実行した際は、メインエージェントが `/memories/workflow_notes.md` を読み、そこに書かれた形式の中国語レポートを委任した。
- `news.db` と `skills/` は起動したディレクトリからの相対パスで解決される。別のディレクトリで実行すると、そこに別の `news.db` が作られ、Skill も 1 つも読み込まれない（ログに `path_not_found` が出る）。
- `memory=` は `/memories/preferences.md` だけを読み込み、このファイルを自動では作成しない。エージェントが書く記憶ファイルの名前はモデルが決める。2026-10-29 の実行では `/memories/workflow_notes.md` に書き込まれ、このファイルは `memory=` では読み込まれない。ただし 2026-11-26 の実行のように、メインエージェントが `ls` と `read_file` で読むことはある。
- 承認を通さない場合、モデルが `/report/` と `/memories/` に書き込むパスと内容を人間が確認しない。
- `news-collector` の 10 件という上限はプロンプトにしか書いていない。2026-11-02 の実行では 20 件を収集した。
- `interrupt_on` を有効にした場合、`python agent.py` の Checkpointer は `MemorySaver` なので、中断状態はプロセスのメモリにしかない。一時停止中にプログラムを終了すると、その実行は再開できない。
- `interrupt_on` を有効にした場合、再開ループは `result.interrupts` の最初の中断しか処理しない。複数のサブエージェントが並行して書き込み、同時に複数の中断が発生すると、LangGraph は中断 ID ごとに再開値を求めるため、現在のコードではエラーになる。
- `read_file` はデフォルトで 100 行を読む。履歴が 100 行を超えると、モデルがページ単位で読まない限り最初の 100 行としか照合しない。
- `langgraph dev` はプロジェクト内の `.py` ファイルが変わると再読み込みし、実行中の run は中断される。2026-11-26 の実行では、実行中に `demo_users.py` を作成したため `demo.py` のストリームが切れ、7 項目中 4 項目が不合格になった。
- `langgraph dev` を停止しても実行中の run は終わらず、次の起動時に再開される。2026-11-26 には、サーバー停止の直前に `action=interrupt` で取り消した run が再起動後に再開し、新しい `news.db` に書き込んだ。サーバーを止める前に、`busy` のスレッドがないことを確認する。

## 参考

- [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action): Datawhale のオープンソース講座。CC BY-NC-SA 4.0 ライセンス
- [Deep Agents 公式ドキュメント](https://docs.langchain.com/oss/python/deepagents/overview)
