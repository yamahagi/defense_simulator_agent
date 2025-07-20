from src.definitions.predefined_japanese_defenses import (
    Fortress, fortress_kadena)
from src.simulations.models import (EnemyUnit, ExpendableWeapon,
                                             Jammer, Weapon)

# 新しい弾薬定義
chinese_missile = ExpendableWeapon(
    name="ChineseMissile",
    cost_per_unit=150,
    move_distance_per_turn=200
)
chinese_torpedo = ExpendableWeapon("ChineseTorpedo", cost_per_unit=100, move_distance_per_turn=150)

# 新しい武器定義
def make_chinese_drone():
    return Jammer("Chinese Drone", range_=500, jam_turns=3, move_distance_per_turn=200,
                  cost=5000, hp=50)

def make_chinese_jets():
    return Weapon("Chinese Jet", range_=300, power=100, move_distance_per_turn=300,
                  cost=8000, hp=80, ammo_type="ChineseMissile", ammo_per_shot=1)

def make_chinese_submarine():
    return Weapon("Chinese Submarine", range_=200, power=160, move_distance_per_turn=100,
                  cost=60000, hp=200, ammo_type="ChineseTorpedo", ammo_per_shot=4)

# 敵ユニットの作成
enemy_unit = EnemyUnit(
    name="Chinese Task Force",
    target_base=fortress_kadena,
    latitude=26.7589,
    longitude=127.7681,
    speed=50,
    weapon_stock={
        "Chinese Drone": [make_chinese_drone() for _ in range(10)],
        "Chinese Jet": [make_chinese_jets() for _ in range(20)],
        "Chinese Submarine": [make_chinese_submarine() for _ in range(5)]
    },
    ammo_stock={
        "ChineseMissile": 300,
        "ChineseTorpedo": 100
    },
    ammo_defs={
        "ChineseMissile": chinese_missile,
        "ChineseTorpedo": chinese_torpedo
    },
    retreat_cost_threshold=30000
)
