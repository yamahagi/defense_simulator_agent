# 防衛戦略シミュレーションエージェント

このプロジェクトは、**専守防衛**に基づいた日本の防衛政策を支援するための、軍事シナリオ生成・戦闘シミュレーション・メタレビュー分析を一貫して行うエージェントシステムです。

## 📌 全体フロー

以下の5ステップで実行します：

1. **シナリオ生成**（`src/scenerio_generator.py`）  
   └ 最新ニュースと防衛拠点情報から敵性国家の軍事シナリオを生成します。

2. **敵ユニット生成**（`src/enemyunit_generator.py`）  
   └ 各シナリオに基づき、敵ユニット（EnemyUnit）を構成する `.py` ファイルを自動生成します。

3. **シミュレーション実行**（`src/run_simulation.sh`）  
   └ 各敵ユニットごとに防衛拠点との戦闘を最大10ターン行い、結果をログ出力します。

4. **戦況分析**（`src/analysis_simulation_result.py`）  
   └ 各作戦のシナリオ・敵・自軍の行動と結果を要約・分析します。

5. **政策メタレビュー**（`src/meta_review.py`）  
   └ 防衛白書資料と国民感情を踏まえた軍事政策レビューを自動生成します。

---

## 🏗️ セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/defense-simulation-agent.git
cd defense-simulation-agent
```

### 2. Python 環境構築

```bash
pip install -r requirements.txt
```

## 💻 実行手順

```bash
export OPENAI_API_KEY = <YOUR OPENAI KEY>
export PYTHONPATH="./":$PYTHONPATH
python src/scenerio_generator.py
python src/enemyunit_generator.py
bash src/run_simulation.sh
python src/analysis_simulation_result.py
python src/meta_review.py
```

## 📂 出力ディレクトリ構成

```bash
results/
├── scenarios.jsonl                    # 生成されたシナリオ（JSON Lines）
├── enemy_units/                       # 自動生成された敵ユニットコード
├── simulation_logs/<作戦名>/         # 各シミュレーションの詳細ログ
├── simulation_analysis_result/        # 要約された戦況レポート
└── meta_review_result/                # 最終政策提案ドキュメント
```
