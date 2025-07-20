import json
import re

from src.simulations.models import ExpendableWeapon, Fortress, Weapon
from src.utils.llm import call_chatgpt

ENEMY_UNIT_PROMPT_TEMPLATE = """
あなたは軍事アナリストでありエンジニアです。
以下のシナリオをもとにmodels.pyのEnemyUnitの初期化パラメータを作成してくださいweapon_stock、ammo_stock、ammo_defsに関しては敵国独自のものを使用してください。
Jammer以外のWeaponのammo_typeに関しては必ず何かしら一つは指定してください。ammo_stock、ammo_typeを定義せずにWeaponを定義することはできません
predefined_japanese_defenses.pyクラス定義を参考にして、同様のファイルとして読み込めるようにコードだけを出してください。
他の説明などは何も出力しないでください。攻撃対象のbaseにはpredefined_japanese_defenses.pyで定義されているFortressを使用してください。
EnemyUnitはsrc.simulations.modelsからimportして、japanese fortressはsrc.definitions.predefined_japanese_defensesからimportしてください
そのほかのmodels.pyで定義されている様々な武器クラスもsrc.simulations.modelsからimportしてください。
retreat_cost_thresholdはWeaponのコストとシナリオの目的や戦力投入レベルを参照して設定してください。
基本的にはweaponが一個壊されたらその分のコストが加算されるのと、そのweaponを使うたびに対応するammo分のコストも追加されます。
もし戦力投入レベルが高い場合は武器がかなり壊されても退却しないように設定し、低い場合は武器が壊れるのをあまり好まないように設定してください。
敵のunitは一つだけ設定し、変数名はenemy_unitで固定してください。また、緯度、経度はtarget_baseから100km以内に収まるようにかなり近いものにしてください。
具体的にはtarget baseの緯度、経度からそれぞれ1度以上離れないようにしてください。


## シナリオ
{scenario}

## predefined_japanese_defenses.py
{predefined_japanese_defenses}

## models.py
{models}
"""


def summarize_fortresses(fortresses: list[Fortress]) -> str:
    lines = []
    for f in fortresses:
        weapon_summary = ', '.join(
            f"{wname}（{len(wlist)}）"
            for wname, wlist in f.weapon_stock.items()
        )
        lines.append(
            f"- {f.name} (位置: {f.latitude},{f.longitude}, 保有武器: {weapon_summary or 'なし'})"
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

def generate_enemy_unit(scenario) -> str:
    predefined_japanese_defenses = open("src/definitions/predefined_japanese_defenses.py").read()
    models = open("src/simulations/models.py").read()
    prompt = ENEMY_UNIT_PROMPT_TEMPLATE.format(scenario=scenario, predefined_japanese_defenses=predefined_japanese_defenses, models=models)

    response = call_chatgpt(
        messages=[{"role": "user", "content": prompt}],
    )
    return re.sub(r"^```python\s*|```$", "", response.strip(), flags=re.MULTILINE)

if __name__ == "__main__":
    # Fortressとニュースを取得
    with open("results/scenarios.jsonl") as f:
        scenarios = [json.loads(line) for line in f]
    for scenario in scenarios:
        print(scenario)
        enemy_unit = generate_enemy_unit(scenario=scenario)
        with open(f"results/enemy_units/{scenario['作戦名']}.py", "w") as fw:
            fw.write(enemy_unit)
        