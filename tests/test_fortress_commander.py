from results.enemy_units.天空の盾 import enemy_unit
from src.definitions.predefined_japanese_defenses import (fortress_amami,
                                                          fortress_kadena,
                                                          fortress_kanoya,
                                                          fortress_naha,
                                                          fortress_sasebo)
from src.simulations.models import FortressCommander

fortress_commander = FortressCommander(fortress_naha, enemy_unit, [fortress_naha, fortress_amami, fortress_sasebo, fortress_kadena, fortress_kanoya], enemy_goal="日中双方の緊張が最高潮に達する中、南鳥島周辺で中国が調査活動を強行し、実効支配を目指す。奄美前進基地を拠点とする拠点制圧を試みる。")
print(fortress_commander.decide_action(1, []))

fortress_commander = FortressCommander(fortress_amami, enemy_unit, [fortress_naha, fortress_amami, fortress_sasebo, fortress_kadena, fortress_kanoya], enemy_goal="日中双方の緊張が最高潮に達する中、南鳥島周辺で中国が調査活動を強行し、実効支配を目指す。奄美前進基地を拠点とする拠点制圧を試みる。")
print(fortress_commander.decide_action(1, []))