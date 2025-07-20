from src.definitions.predefined_japanese_defenses import fortress_naha
from src.simulations.models import EnemyUnit, ExpendableWeapon, Weapon

# 新しい弾薬定義
long_range_missile_chinese = ExpendableWeapon(
    name="LongRangeMissileCHN",
    cost_per_unit=180,
    move_distance_per_turn=200
)
torpedo_chinese = ExpendableWeapon("TorpedoCHN", cost_per_unit=180, move_distance_per_turn=200)

# 新しい武器定義
def make_f35b_chinese():
    return Weapon("F-35B", range_=140, power=110, move_distance_per_turn=100,
                  cost=15000, hp=100, ammo_type="LongRangeMissileCHN", ammo_per_shot=1)

def make_izumo_chinese():
    return Weapon("Izumo-class Destroyer", range_=230, power=170, move_distance_per_turn=120,
                  cost=110000, hp=250, ammo_type="LongRangeMissileCHN", ammo_per_shot=4)

def make_atago_chinese():
    return Weapon("Atago-class Aegis", range_=280, power=190, move_distance_per_turn=130,
                  cost=140000, hp=300, ammo_type="LongRangeMissileCHN", ammo_per_shot=6)

def make_oyashio_chinese():
    return Weapon("Oyashio-class Submarine", range_=140, power=140, move_distance_per_turn=140,
                  cost=48000, hp=120, ammo_type="TorpedoCHN", ammo_per_shot=2)

# 敵ユニットの定義
enemy_unit = EnemyUnit(
    name="Chinese Task Force",
    target_base=fortress_naha,
    latitude=25.8467,  # 近隣の適当な緯度 (那覇基地と1度以上離れない範囲内)
    longitude=127.4221,  # 近隣の適当な経度 (那覇基地と1度以上離れない範囲内)
    speed=15,
    weapon_stock={
        "F-35B": [make_f35b_chinese() for _ in range(16)],
        "Izumo-class Destroyer": [make_izumo_chinese() for _ in range(3)],
        "Oyashio-class Submarine": [make_oyashio_chinese() for _ in range(5)]
    },
    ammo_stock={
        "LongRangeMissileCHN": 400,
        "TorpedoCHN": 180
    },
    ammo_defs={
        "LongRangeMissileCHN": long_range_missile_chinese,
        "TorpedoCHN": torpedo_chinese
    },
    retreat_cost_threshold=700000  # 戦力投入レベルから設定
)
