import json
import sys
from importlib import import_module

from src.definitions.predefined_japanese_defenses import (fortress_amami,
                                                          fortress_kadena,
                                                          fortress_kanoya,
                                                          fortress_naha,
                                                          fortress_sasebo)
from src.simulations.models import Simulation


def main(enemy_code_name: str):
    # 動的 import（例：results.enemy_units.天空の盾）
    module_path = f"results.enemy_units.{enemy_code_name}"
    module = import_module(module_path)

    enemy_unit = getattr(module, "enemy_unit")

    # 対応するシナリオを取得
    datal = [json.loads(line) for line in open("results/scenarios.jsonl", encoding="utf-8")]
    scenario_list = [data for data in datal if data["作戦名"] == enemy_code_name]
    
    if not scenario_list:
        print(f"❌ 作戦名 '{enemy_code_name}' に対応するシナリオが見つかりません")
        return
    
    enemy_scenario = scenario_list[0]

    # シミュレーション実行
    simulator = Simulation(
        fortresses=[fortress_naha, fortress_amami, fortress_sasebo, fortress_kadena, fortress_kanoya],
        enemy_unit=enemy_unit,
        enemy_scenario=enemy_scenario,
        max_turns=10
    )
    simulator.run()
    simulator.export_results(output_dir=f"results/simulation_logs/{enemy_scenario['作戦名']}")
    print(f"✅ 完了: {enemy_code_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python run_simulation_template.py <作戦名>")
        sys.exit(1)
    main(sys.argv[1])
