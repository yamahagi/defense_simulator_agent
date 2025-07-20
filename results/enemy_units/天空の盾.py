from src.definitions.predefined_japanese_defenses import \
    fortress_amami
from src.simulations.models import EnemyUnit, ExpendableWeapon, Weapon

# 新しい弾薬定義
intermediate_range_missile = ExpendableWeapon(
    name="IntermediateRangeMissile",
    cost_per_unit=150,  # 仮の価格
    move_distance_per_turn=180
)
anti_air_missile = ExpendableWeapon(
    name="AntiAirMissile",
    cost_per_unit=100,  # 仮の価格
    move_distance_per_turn=150
)

# 新しい武器定義
# J-20戦闘機
def make_j20():
    return Weapon(
        name="J-20 Fighter",
        range_=200,
        power=130,
        move_distance_per_turn=140,
        cost=16000,
        hp=120,
        ammo_type="IntermediateRangeMissile",
        ammo_per_shot=2
    )

# Type 055駆逐艦
def make_type_055():
    return Weapon(
        name="Type 055 Destroyer",
        range_=300,
        power=220,
        move_distance_per_turn=150,
        cost=120000,
        hp=300,
        ammo_type="IntermediateRangeMissile",
        ammo_per_shot=4
    )

# HQ-9地対空ミサイル
def make_hq9():
    return Weapon(
        name="HQ-9 SAM",
        range_=200,
        power=150,
        move_distance_per_turn=100,
        cost=5000,
        hp=100,
        ammo_type="AntiAirMissile",
        ammo_per_shot=1
    )

# 敵ユニット
enemy_unit = EnemyUnit(
    name="Chinese Assault Fleet",
    target_base=fortress_amami,
    latitude=27.5000,
    longitude=129.0000,
    speed=30,
    weapon_stock={
        "J-20 Fighter": [make_j20() for _ in range(24)],
        "Type 055 Destroyer": [make_type_055() for _ in range(6)],
        "HQ-9 SAM": [make_hq9() for _ in range(8)]
    },
    ammo_stock={
        "IntermediateRangeMissile": 800,
        "AntiAirMissile": 400
    },
    ammo_defs={
        "IntermediateRangeMissile": intermediate_range_missile,
        "AntiAirMissile": anti_air_missile
    },
    retreat_cost_threshold=500000  # 高い戦力投入レベルを反映
)
