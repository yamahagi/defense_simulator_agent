from results.enemy_units.風の刃 import enemy_unit
from src.definitions.predefined_japanese_defenses import (fortress_amami,
                                                          fortress_kadena,
                                                          fortress_kanoya,
                                                          fortress_naha,
                                                          fortress_sasebo)
from src.simulations.models import EnemyCommander

enemy_commander = EnemyCommander(enemy_unit, [fortress_naha, fortress_amami, fortress_sasebo, fortress_kadena, fortress_kanoya], goal="日中双方の緊張が最高潮に達する中、南鳥島周辺で中国が調査活動を強行し、実効支配を目指す。奄美前進基地を拠点とする拠点制圧を試みる。")
print(enemy_commander.decide_action(1, []))
