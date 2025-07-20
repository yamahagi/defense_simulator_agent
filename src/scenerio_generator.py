import json
import re

from src.definitions.predefined_japanese_defenses import (fortress_amami,
                                                          fortress_kadena,
                                                          fortress_kanoya,
                                                          fortress_naha,
                                                          fortress_sasebo)
from src.simulations.models import ExpendableWeapon, Fortress, Weapon
from src.tools.get_latest_news import GetLatestNewsTool
from src.utils.llm import call_chatgpt

SCENARIO_PROMPT_TEMPLATE = """
あなたは軍事アナリストです。
以下のニュースと日本の防衛拠点の情報を基に、中国などの敵対勢力が起こしうる現実的な軍事シナリオを10個提案してください。

## 制約条件
- シナリオは現実的かつ地理・資源・戦略的文脈に合致すること
- 明確な目的・侵攻手段・対象地域を含むこと
- 対象となるFortress名を1つ含めること（例: "Ishigaki"）
- なるべく多様なシナリオを生成してください。使う装備、目的、緊張度、どれくらいこの侵攻にリソースを注ぐ気があるかなど様々な設定で生成してください。
- 今回はPoCとして戦艦や戦闘機の出動が伴うようなハイリスクなシナリオを重点的に生成してください。
- 以下の出力例のフォーマットに沿ってください。作戦名、目的、手段、戦力投入レベルそれぞれを入れてください。
- シナリオは出力例以上になるべくできる限り詳細に記述してください。

## 出力例:
【軍事シナリオ1】
作戦名: 赤礁鉄雷
目的: 2025年7月初旬、日本の南鳥島近海にて確認された大規模なレアメタル鉱床の発見を契機に、中国は同地域の実効支配を既成事実化するための強硬な軍事行動に踏み切った。南鳥島沖合のマンガンノジュール資源確保を目的に、中国は小規模ながら高度に自律的な無人水上艦隊（UFA）を派遣し、夜間に石垣島（Ishigaki）Fortressを攻撃。目標は日本の哨戒監視能力の一時的無力化と、同時並行での「調査名目」EEZ侵入による実効支配の既成事実化。
手段: 高速UFAによるレーダー攪乱→Cannon・SAM陣地への精密射撃→調査船団の投入
戦力投入レベル: 低～中（限定的な艦隊）。損害が大きくなりそうな場合は早めに撤退する可能性がある。また、アメリカなどの世論の反発が大きくなった場合も早めに撤退する可能性がある

【軍事シナリオ2】
...

## ニュース
{news_text}

## 日本の防衛拠点一覧
{fortress_summary}
"""

def summarize_fortresses(fortresses: list[Fortress]) -> str:
    lines = []
    for f in fortresses:
        weapon_summary = ', '.join(
            f"{wname}（{len(wlist)}）"
            for wname, wlist in f.weapon_stock.items()
        )
        lines.append(
            f"- {f.name} (緯度経度: {f.latitude},{f.longitude}, 保有武器: {weapon_summary or 'なし'})"
        )
    return "\n".join(lines)

def load_fortresses_from_file(path: str) -> list[Fortress]:
    with open(path, "r") as f:
        data = json.load(f)

    fortresses = []
    for fd in data:
        ammo_defs = {
            name: ExpendableWeapon(name, **props)
            for name, props in fd["ammo_defs"].items()
        }
        weapons = {
            wname: [
                Weapon(name=w["name"], range_=w["range_"], power=w["power"],
                       move_distance_per_turn=w["move_distance_per_turn"], cost=w["cost"],
                       hp=w["hp"], ammo_type=w["ammo_type"], ammo_per_shot=w["ammo_per_shot"])
                for w in wlist
            ]
            for wname, wlist in fd["weapon_stock"].items()
        }

        fortresses.append(Fortress(
            name=fd["name"], latitude=fd["latitude"], longitude=fd["longitude"], weapon_stock=weapons, ammo_stock=fd["ammo_stock"], ammo_defs=ammo_defs
        ))
    return fortresses


def extract_scenearios(text: str) -> list[dict]:
    scenario_blocks = re.split(r'(【軍事シナリオ\d+】)', text)
    scenarios = []

    # 2つずつ（ラベルと本文）処理
    for i in range(1, len(scenario_blocks), 2):
        label = scenario_blocks[i].strip()
        content = scenario_blocks[i + 1]

        data = {
            "シナリオID": label,
            "作戦名": None,
            "目的": None,
            "手段": None,
            "戦力投入レベル": None
        }

        for key in ["作戦名", "目的", "手段", "戦力投入レベル"]:
            pattern = rf'{key}:\s*(.+?)(?=\n\S|$)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                data[key] = match.group(1).strip()

        scenarios.append(data)
    return scenarios

def generate_natural_scenarios(news_text: str, fortresses: list[Fortress]) -> str:
    fortress_summary = summarize_fortresses(fortresses)
    prompt = SCENARIO_PROMPT_TEMPLATE.format(news_text=news_text, fortress_summary=fortress_summary)
    print(prompt)

    response = call_chatgpt(
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.strip()
    return extract_scenearios(content)

if __name__ == "__main__":
    # Fortressとニュースを取得
    fortresses = [
        fortress_naha,
        fortress_amami,
        fortress_sasebo,
        fortress_kadena,
        fortress_kanoya,
    ]
    news = GetLatestNewsTool().use_tool("南西諸島")

    # シナリオ生成
    scenarios = generate_natural_scenarios(news, fortresses)
    print("=== 作戦シナリオ ===")
    print(scenarios)
    with open("results/scenarios.jsonl", "w") as fw:
        for scenario in scenarios:
            fw.write(json.dumps(scenario, ensure_ascii=False) + "\n")
