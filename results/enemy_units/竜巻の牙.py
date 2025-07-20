from src.definitions.predefined_japanese_defenses import \
    fortress_sasebo
from src.simulations.models import EnemyUnit, ExpendableWeapon, Weapon

# 敵国の弾薬定義
enemy_long_range_missile = ExpendableWeapon(
    name="EnemyLongRangeMissile",
    cost_per_unit=180,  # 約1.8億円
    move_distance_per_turn=200
)
enemy_torpedo = ExpendableWeapon(
    name="EnemyTorpedo",
    cost_per_unit=180,
    move_distance_per_turn=200
)

# 敵国の武器定義
def make_enemy_destroyer():
    return Weapon(
        name="Enemy Destroyer",
        range_=300,
        power=220,
        move_distance_per_turn=120,
        cost=130000,
        hp=300,
        ammo_type="EnemyLongRangeMissile",
        ammo_per_shot=6
    )

def make_enemy_submarine():
    return Weapon(
        name="Enemy Submarine",
        range_=150,
        power=160,
        move_distance_per_turn=140,
        cost=60000,
        hp=130,
        ammo_type="EnemyTorpedo",
        ammo_per_shot=2
    )

# 敵ユニットの定義
enemy_unit = EnemyUnit(
    name="Enemy Task Force",
    target_base=fortress_sasebo,
    latitude=32.5,
    longitude=129.5,
    speed=100,
    weapon_stock={
        "Enemy Destroyer": [make_enemy_destroyer() for _ in range(8)],
        "Enemy Submarine": [make_enemy_submarine() for _ in range(10)]
    },
    ammo_stock={
        "EnemyLongRangeMissile": 400,
        "EnemyTorpedo": 250
    },
    ammo_defs={
        "EnemyLongRangeMissile": enemy_long_range_missile,
        "EnemyTorpedo": enemy_torpedo
    },
    retreat_cost_threshold=500000  # 大規模攻撃のため閾値は高く設定
)
