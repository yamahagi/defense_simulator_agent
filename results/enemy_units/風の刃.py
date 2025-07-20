from src.definitions.predefined_japanese_defenses import \
    fortress_amami
from src.simulations.models import (EnemyUnit, ExpendableWeapon,
                                             Jammer, Weapon)

# 定義される武器と弾薬
light_flare = ExpendableWeapon(name="LightFlare", cost_per_unit=5, move_distance_per_turn=100)
stealth_missile = ExpendableWeapon(name="StealthMissile", cost_per_unit=150, move_distance_per_turn=200)

# 武器の定義
def stealth_corvette():
    return Weapon(name="Stealth Corvette", range_=150, power=100, move_distance_per_turn=50,
                  cost=75000, hp=150, ammo_type="StealthMissile", ammo_per_shot=1)

def fast_recon_boat():
    return Weapon(name="Fast Recon Boat", range_=50, power=30, move_distance_per_turn=80,
                  cost=5000, hp=40, ammo_type="LightFlare", ammo_per_shot=1)

def jammer():
    return Jammer(name="Signal Jammer", range_=100, jam_turns=2, move_distance_per_turn=40,
                  cost=10000, hp=50)

# 敵ユニットの初期化
enemy_unit = EnemyUnit(
    name="Stealth Operations Unit",
    target_base=fortress_amami,
    latitude=fortress_amami.latitude + 0.5,
    longitude=fortress_amami.longitude - 0.5,
    speed=40,
    weapon_stock={
        "Stealth Corvette": [stealth_corvette() for _ in range(3)],
        "Fast Recon Boat": [fast_recon_boat() for _ in range(5)],
        "Signal Jammer": [jammer() for _ in range(2)],
    },
    ammo_stock={
        "StealthMissile": 50,
        "LightFlare": 100,
    },
    ammo_defs={
        "StealthMissile": stealth_missile,
        "LightFlare": light_flare,
    },
    retreat_cost_threshold=40000
)
