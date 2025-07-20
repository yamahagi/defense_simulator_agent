from src.definitions.predefined_japanese_defenses import \
    fortress_amami
from src.simulations.models import EnemyUnit, ExpendableWeapon, Weapon

long_range_missile = ExpendableWeapon(
    name="LongRangeMissile",
    cost_per_unit=250,  # Placeholder cost for Chinese missile
    move_distance_per_turn=200
)
medium_range_missile = ExpendableWeapon(
    name="MediumRangeMissile",
    cost_per_unit=100,
    move_distance_per_turn=150
)

def make_chinese_destroyer():
    return Weapon("Type 052D Destroyer", range_=300, power=220, move_distance_per_turn=100,
                  cost=140000, hp=270, ammo_type="LongRangeMissile", ammo_per_shot=4)

def make_chinese_stealth_uav():
    return Weapon("Stealth UAV", range_=150, power=60, move_distance_per_turn=100,
                  cost=2000, hp=50, ammo_type="MediumRangeMissile", ammo_per_shot=2)

enemy_unit = EnemyUnit(
    name="Chinese Naval Task Force",
    target_base=fortress_amami,
    latitude=28.3,
    longitude=129.5,
    speed=25,
    weapon_stock={
        "Type 052D Destroyer": [make_chinese_destroyer() for _ in range(6)],
        "Stealth UAV": [make_chinese_stealth_uav() for _ in range(10)]
    },
    ammo_stock={
        "LongRangeMissile": 300,
        "MediumRangeMissile": 200
    },
    ammo_defs={
        "LongRangeMissile": long_range_missile,
        "MediumRangeMissile": medium_range_missile
    },
    retreat_cost_threshold=500000  # Considering a moderate level of commitment and potential losses
)
