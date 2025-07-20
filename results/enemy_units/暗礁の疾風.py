from src.definitions.predefined_japanese_defenses import \
    fortress_kanoya
from src.simulations.models import EnemyUnit, ExpendableWeapon, Weapon

# 敵国独自の弾薬定義
enemy_long_range_missile = ExpendableWeapon(
    name="EnemyLongRangeMissile",
    cost_per_unit=150,  # （価格を独自に設定）
    move_distance_per_turn=200
)

enemy_torpedo = ExpendableWeapon(
    name="EnemyTorpedo",
    cost_per_unit=150,  # （価格を独自に設定）
    move_distance_per_turn=200
)

# 敵国独自の武器定義
def make_enemy_stealth_submarine():
    return Weapon(
        name="EnemyStealthSubmarine",
        range_=200, 
        power=150, 
        move_distance_per_turn=100,
        cost=80000, 
        hp=150, 
        ammo_type="EnemyTorpedo", 
        ammo_per_shot=2
    )

# 敵ユニットの定義
enemy_unit = EnemyUnit(
    name="Enemy Stealth Fleet",
    target_base=fortress_kanoya,
    latitude=31.0,  # 近い位置（緯度）
    longitude=130.5,  # 近い位置（経度）
    speed=100,
    weapon_stock={
        "EnemyStealthSubmarine": [make_enemy_stealth_submarine() for _ in range(5)],
    },
    ammo_stock={
        "EnemyLongRangeMissile": 100,
        "EnemyTorpedo": 100
    },
    ammo_defs={
        "EnemyLongRangeMissile": enemy_long_range_missile,
        "EnemyTorpedo": enemy_torpedo
    },
    retreat_cost_threshold=5000  # 戦力投入レベルが低～中範囲で設定
)
