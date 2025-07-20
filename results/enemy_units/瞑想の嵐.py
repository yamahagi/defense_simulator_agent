from src.definitions.predefined_japanese_defenses import \
    fortress_kadena
from src.simulations.models import EnemyUnit, ExpendableWeapon, Weapon

# 敵国独自の弾薬定義
enemy_long_range_missile = ExpendableWeapon(
    name="EnemyLongRangeMissile",
    cost_per_unit=180,  # 単位あたりのコスト（100万円）
    move_distance_per_turn=180
)

enemy_torpedo = ExpendableWeapon(
    name="EnemyTorpedo",
    cost_per_unit=160,  # 単位あたりのコスト（100万円）
    move_distance_per_turn=180
)

# 敵国独自の武器定義
def make_enemy_destroyer():
    return Weapon(
        name="Enemy Destroyer",
        range_=250,
        power=190,
        move_distance_per_turn=120,
        cost=110000,
        hp=240,
        ammo_type="EnemyLongRangeMissile",
        ammo_per_shot=4
    )

def make_enemy_submarine():
    return Weapon(
        name="Enemy Submarine",
        range_=150,
        power=160,
        move_distance_per_turn=140,
        cost=52000,
        hp=130,
        ammo_type="EnemyTorpedo",
        ammo_per_shot=2
    )

# 敵ユニットの初期化
enemy_unit = EnemyUnit(
    name="Enemy Fleet Unit",
    target_base=fortress_kadena,
    latitude=26.3,  # 緯度（Kadenaから1度以内）
    longitude=127.7,  # 経度（Kadenaから1度以内）
    speed=100,  # 移動速度
    weapon_stock={
        "Enemy Destroyer": [make_enemy_destroyer() for _ in range(2)],
        "Enemy Submarine": [make_enemy_submarine() for _ in range(3)],
    },
    ammo_stock={
        "EnemyLongRangeMissile": 400,
        "EnemyTorpedo": 200,
    },
    ammo_defs={
        "EnemyLongRangeMissile": enemy_long_range_missile,
        "EnemyTorpedo": enemy_torpedo,
    },
    retreat_cost_threshold=450000  # 45億円
)
