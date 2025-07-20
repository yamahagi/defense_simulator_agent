import json

from results.enemy_units.天空の盾 import enemy_unit
from src.definitions.predefined_japanese_defenses import (fortress_amami,
                                                          fortress_kadena,
                                                          fortress_kanoya,
                                                          fortress_naha,
                                                          fortress_sasebo)
from src.simulations.models import Simulation

datal = [json.loads(line) for line in open("results/scenarios.jsonl")]
enemy_scenario = [data for data in datal if data["作戦名"] == "天空の盾"]
simulator = Simulation(fortresses=[fortress_naha, fortress_amami, fortress_sasebo, fortress_kadena, fortress_kanoya], enemy_unit=enemy_unit, enemy_scenario=enemy_scenario, max_turns=3)
simulator.run()
simulator.export_results(output_dir=f"logs/{enemy_scenario['作戦名']}")
