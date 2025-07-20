import glob
import json
import os

from src.utils.llm import call_chatgpt


# 1. results配下の*.txtからシナリオ情報を抽出し、検索クエリ生成
def load_scenarios_and_generate_queries(results_dir="results/simulation_analysis_result/"):
    scenario_files = glob.glob(os.path.join(results_dir, "*_summary.txt"))
    scenarios = []
    queries_list = []
    for filepath in scenario_files:
        with open(filepath, "r", encoding="utf-8") as f:
            scenario_text = f.read().strip()
            scenarios.append({"file": os.path.basename(filepath), "text": scenario_text})
            # ChatGPTにクエリ生成依頼
            prompt = (
                "以下は軍事シミュレーションの要約です。この内容に基づき、防衛白書（防衛省が発行する公式文書）から取得すべき関連軍事情報を検索するための日本語の検索クエリをカンマ区切りの単語のリスト(e.g. ロシア,中国,北朝鮮)として出力してください。\n\n"
                f"【シナリオ要約】\n{scenario_text}\n\n"
                "【出力形式】\n- カンマ区切りの単語のリスト"
            )
            response = call_chatgpt(
                 messages=[
                    {"role": "system", "content": "あなたは防衛政策の専門家であり、日本語で簡潔な検索クエリを出力します。"},
                    {"role": "user", "content": prompt}
                ]
            )
            # 1行目だけをクエリとみなす（先頭の"- "などを除く）
            queries = response.strip().split(",")
            queries_list.append(queries)
    return scenarios, queries_list


# 2. 検索クエリに基づきresources/defense_of_japan/R06shiryo.jsonlを検索（単純なキーワードマッチ）
def search_defense_documents(queries_list, defense_file="resources/defense_of_japan/R06shiryo.jsonl"):
    with open(defense_file, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    defenses_list = []
    for queries in queries_list:
        search_results_list = []
        for entry in data:
            hit_num = 0
            for query in queries:
                if query in entry:
                    hit_num += 1
            search_results_list.append((entry, hit_num))
        defenses_list.append([search_result[0] for search_result in sorted(search_results_list, key=lambda x: x[1])[::-1]][:3])
    return defenses_list

# 3. 最新ニュースと国民感情の読み込み
def load_contextual_info(news_path="resources/latest_news.txt", emotion_path="resources/national_emotion/passive.txt"):
    with open(news_path, "r", encoding="utf-8") as f:
        news = f.read().strip()
    with open(emotion_path, "r", encoding="utf-8") as f:
        emotion = f.read().strip()
    return news, emotion

# 4. プロンプト作成とAPIリクエスト送信
def build_prompt_and_request_gpt(scenarios, defense_results, news, emotion):
    prompt = (
        "これは「専守防衛を指向した軍事シミュレーションによる防衛戦略の策定エージェント」における最終工程の軍事政策のメタレビューです。\n\n"
        "### 現在の状況\n"
        f"【直近のニュース】\n{news}\n\n"
        f"【軍事政策をめぐる国民感情】\n{emotion}\n\n"
        "### シナリオ概要と結果\n"
    )
    for i, scenario in enumerate(scenarios):
        prompt += f"■ シナリオ {i+1}: {scenario['file']}\n"
        prompt += f"- 要約: {scenario['text']}...\n"
        prompt += f"- 関連防衛資料（最大3件）:\n"
        for doc in defense_results[i]:
            prompt += f"    - p.{doc['page']}: {doc['text']}...\n"
        prompt += "\n"

    prompt += (
        "### メタレビューと最終提案\n"
        "各シナリオにおける現実度、日本の防衛政策・国民感情との整合性を踏まえ、最適な軍事政策の提案をまとめてください。"
        "各シナリオや関連防衛資料についても触れながらなるべく詳細に報告書として書いてください。各シナリオの詳細を書く必要はないですが、どのようなシナリオがあったかについてはシナリオ名などを挙げながら軽く触れてくだしあ。出力は関連文書(防衛白書)に書かれているような文体で5000-6000文字でお願いします。\n\n"
        "国民感情や直近のニュースについても触れ、今回提案した軍事政策が日本の専守防衛を中心とした防衛政策と照らしわせて世論や他国にどう受け入れられるか、専守防衛の原則を逸脱していないかについても詳細に論じてください。"
        "また、最後には上記全体の要約を簡潔にまとめてください。\n"
    )
    response = call_chatgpt(
            messages=[
            {"role": "system", "content": "あなたは日本の防衛政策に詳しい専門家として、政府に防衛政策の提案資料を書いています。"},
            {"role": "user", "content": prompt}
        ],
    )
    return response

# 5. レスポンスを保存
def save_output(content, output_dir="results/meta_review_result", emotion="passive"):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"meta_review_output_{emotion}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path

# 実行関数
def main():
    scenarios, queries = load_scenarios_and_generate_queries()
    defense_results = search_defense_documents(queries)
    news, emotion = load_contextual_info()
    response = build_prompt_and_request_gpt(scenarios, defense_results, news, emotion)
    path = save_output(response)
    print(f"✅ メタレビュー結果を保存しました: {path}")

if __name__ == "__main__":
    main()
