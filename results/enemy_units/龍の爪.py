from src.definitions.predefined_japanese_defenses import \
    fortress_kanoya
from src.simulations.models import (EnemyUnit, ExpendableWeapon,
                                             Jammer, Weapon)

# 新しい弾薬定義
advanced_torpedo = ExpendableWeapon(name="AdvancedTorpedo", cost_per_unit=250, move_distance_per_turn=220)

# 新しい武器定義
def make_destroyer():
    return Weapon(
        name="Advanced Destroyer",
        range_=300, 
        power=220, 
        move_distance_per_turn=150,
        cost=180000, 
        hp=320, 
        ammo_type="AdvancedTorpedo", 
        ammo_per_shot=8
    )

def make_jammer():
    return Jammer(
        name="StealthJammer",
        range_=300,
        jam_turns=3,
        move_distance_per_turn=160,
        cost=50000,
        hp=100
    )

# 敵ユニットの初期化
enemy_unit = EnemyUnit(
    name="Dragon Claw Command Unit",
    target_base=fortress_kanoya,
    latitude=31.0000,
    longitude=130.5000,
    speed=150,
    weapon_stock={
        "Advanced Destroyer": [make_destroyer() for _ in range(3)],
        "StealthJammer": [make_jammer() for _ in range(2)]
    },
    ammo_stock={"AdvancedTorpedo": 160},
    ammo_defs={"AdvancedTorpedo": advanced_torpedo},
    retreat_cost_threshold=500000  # 高戦力投入のため高めのしきい値を設定
)
