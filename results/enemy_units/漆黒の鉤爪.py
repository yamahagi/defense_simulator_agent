from src.definitions.predefined_japanese_defenses import \
    fortress_sasebo
from src.simulations.models import EnemyUnit, ExpendableWeapon, Weapon

# 敵国独自の弾薬定義
cruise_missile = ExpendableWeapon(
    name="CruiseMissile",
    cost_per_unit=250,  # 約2億5000万円
    move_distance_per_turn=100
)

stealth_torpedo = ExpendableWeapon(
    name="StealthTorpedo",
    cost_per_unit=220,  # 約2億2000万円
    move_distance_per_turn=150
)

# 敵国独自の武器定義
def make_stealth_bomber():
    return Weapon(
        name="Stealth Bomber",
        range_=300,
        power=250,
        move_distance_per_turn=180,
        cost=300000,
        hp=150,
        ammo_type="CruiseMissile",
        ammo_per_shot=2
    )

def make_silent_submarine():
    return Weapon(
        name="Silent Submarine",
        range_=200,
        power=180,
        move_distance_per_turn=140,
        cost=75000,
        hp=100,
        ammo_type="StealthTorpedo",
        ammo_per_shot=1
    )

# 敵ユニットの定義
enemy_unit = EnemyUnit(
    name="Black Claw",
    target_base=fortress_sasebo,
    latitude=33.1,  # 配置位置をターゲット基地から1度以内に設定
    longitude=129.6,
    speed=100,
    weapon_stock={
        "Stealth Bomber": [make_stealth_bomber() for _ in range(5)],
        "Silent Submarine": [make_silent_submarine() for _ in range(3)]
    },
    ammo_stock={
        "CruiseMissile": 20,
        "StealthTorpedo": 15
    },
    ammo_defs={
        "CruiseMissile": cruise_missile,
        "StealthTorpedo": stealth_torpedo
    },
    retreat_cost_threshold=800000  # 高戦力投入レベルを考慮して設定
)
