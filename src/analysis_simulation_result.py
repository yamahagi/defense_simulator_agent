import json
import os

from src.utils.llm import call_chatgpt


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_jsonl(path):
    scenario_info_map = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            name = record.get("作戦名")
            if name:
                scenario_info_map[name] = record
    return scenario_info_map

def summarize_scenario(scenario_name, enemy_data, fortress_data, history_data, scenario_info=None):
    header = f"シナリオ名: {scenario_name}\n\n"
    if scenario_info:
        header += (
            f"【敵視点シナリオ情報】\n"
            f"シナリオID: {scenario_info.get('シナリオID')}\n"
            f"目的: {scenario_info.get('目的')}\n"
            f"手段: {scenario_info.get('手段')}\n"
            f"戦力投入レベル: {scenario_info.get('戦力投入レベル')}\n\n"
        )
    header += (
        "以下の情報は作戦終了後の戦況データです。\n"
        "・'current_cost' はその拠点やユニットの被害総額（単位：100万円）を示します。\n"
        "・'weapon_stock' における 'destroyed' は破壊された武器の数を示します。\n\n"
        f"[敵ユニット情報]\n{json.dumps(enemy_data, indent=2, ensure_ascii=False)}\n\n"
        f"[味方拠点情報]\n{json.dumps(fortress_data, indent=2, ensure_ascii=False)}\n\n"
        f"[作戦履歴]\n{json.dumps(history_data, indent=2, ensure_ascii=False)}\n\n"
        "以下の3つの問いに専門的な視点で答えてください:\n"
        "1. 今回のシナリオ(敵国の目的や戦力投入レベル、自国の軍備配備状況)を要約。ここではまだ戦闘結果は書かない。\n"
        "2. このシナリオの戦闘結果を被害総額も含めて詳細に要約してください。\n"
        "3. なぜそのような戦況となったのか、拠点の行動や配備状況も含めて分析してください。\n"
        "4. 今回の戦闘は敵ユニットを一つだけと限定しましたが、現実では複数の国や部隊が存在します。そのような状況においては今回のシナリオでどのようなことが起き得たかを記述してください。\n"
        "5. もし作戦前に戻れるとすれば、どのような武器やジャマーの使用、もしくは戦略的な配置変更を加えることで、より良い結果を導けたかを提案してください。具体的な武器の名前や、それに必要な予算、立法も含めて提案してください。国としての軍事戦略に使えるレベルで提案してください。もし現在の装備が過剰なのであれば減らす提案もしてください。\n"
    )
    return header

def process_all_logs(base_path="results/simulation_logs", output_dir="results/simulation_analysis_result", scenario_info_path="results/scenarios.jsonl"):
    os.makedirs(output_dir, exist_ok=True)
    scenario_info_map = load_jsonl(scenario_info_path)

    for scenario_name in os.listdir(base_path):
        scenario_path = os.path.join(base_path, scenario_name)
        if os.path.isdir(scenario_path):
            try:
                enemy_path = os.path.join(scenario_path, "result_enemy_unit.json")
                fortress_path = os.path.join(scenario_path, "result_fortresses.json")
                history_path = os.path.join(scenario_path, "result_history.json")

                enemy_data = load_json(enemy_path)
                fortress_data = load_json(fortress_path)
                history_data = load_json(history_path)

                scenario_info = scenario_info_map.get(scenario_name)
                prompt = summarize_scenario(scenario_name, enemy_data, fortress_data, history_data, scenario_info)
                result = call_chatgpt(
                                [
                        {"role": "system", "content": "あなたは軍事戦略分析の専門家です。与えられたシナリオの戦況と結果に基づいて、要因分析と改善策を提案してください。"},
                        {"role": "user", "content": prompt}
                    ]
                )

                output_path = os.path.join(output_dir, f"{scenario_name}_summary.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"{scenario_name} の分析結果を保存しました: {output_path}")

            except Exception as e:
                print(f"[エラー] シナリオ '{scenario_name}' の処理中にエラー: {e}")

if __name__ == "__main__":
    process_all_logs()