from src.simulations.models import ExpendableWeapon, Fortress, Weapon

# 新しい弾薬定義
# 新しい弾薬定義
# 長距離ミサイル（トマホーク）
long_range_missile = ExpendableWeapon(
    name="LongRangeMissile",
    cost_per_unit=200,  # 約2億円（トマホークの価格）
    move_distance_per_turn=200
)
torpedo = ExpendableWeapon("Torpedo", cost_per_unit=200, move_distance_per_turn=200)

# 新しい武器定義（長距離＆海上兵器）

# F-35B（短距離離陸・空母発艦）
def make_f35b():
    return Weapon("F-35B", range_=150, power=120, move_distance_per_turn=100,
              cost=16000, hp=100, ammo_type="LongRangeMissile", ammo_per_shot=1)


# いずも型護衛艦（軽空母転用）
def make_izumo():
    return Weapon("Izumo-class Destroyer", range_=250, power=180, move_distance_per_turn=120,
               cost=120000, hp=250, ammo_type="LongRangeMissile", ammo_per_shot=4)


# あたご型イージス艦
def make_atago():
    return Weapon("Atago-class Aegis", range_=300, power=200, move_distance_per_turn=130,
               cost=150000, hp=300, ammo_type="LongRangeMissile", ammo_per_shot=6)

# おやしお型潜水艦
def make_oyashio():
    return Weapon("Oyashio-class Submarine", range_=150, power=150, move_distance_per_turn=140,
                     cost=50000, hp=120, ammo_type="Torpedo", ammo_per_shot=2)


# 那覇 Air & Naval Base（沖縄県那覇市＋本島南部）
fortress_naha = Fortress(
    name="Naha Air & Naval Base",
    latitude=26.1958,
    longitude=127.6458,
    weapon_stock={
        "F-35B": [make_f35b() for _ in range(12)],
        "Izumo-class Destroyer": [make_izumo() for _ in range(4)],
        "Oyashio-class Submarine": [make_oyashio() for _ in range(8)]
    },
    ammo_stock={
        "LongRangeMissile": 500,
        "Torpedo": 200
    },
    ammo_defs={
        "LongRangeMissile": long_range_missile,
        "Torpedo": torpedo
    },
)

# 奄美 Forward Base（奄美群島）
fortress_amami = Fortress(
    name="Amami Forward Base",
    latitude=28.3589,
    longitude=129.4953,
    weapon_stock={
        "Oyashio-class Submarine": [make_oyashio() for _ in range(10)]
    },
    ammo_stock={"Torpedo": 150},
    ammo_defs={"Torpedo": torpedo},
)

# 佐世保 Naval Base（長崎県・西九州）
fortress_sasebo = Fortress(
    name="Sasebo Naval Base",
    latitude=33.1575,
    longitude=129.7225,
    weapon_stock={
        "Atago-class Aegis": [make_atago() for _ in range(6)],
        "Izumo-class Destroyer": [make_izumo() for _ in range(2)],
        "Oyashio-class Submarine": [make_oyashio() for _ in range(6)]
    },
    ammo_stock={"LongRangeMissile": 800, "Torpedo": 300},
    ammo_defs={"LongRangeMissile": long_range_missile, "Torpedo": torpedo},
)

# 嘉手納 Air-Sea Hub（米軍・沖縄本島中部）
fortress_kadena = Fortress(
    name="Kadena Air-Sea Hub (US)",
    latitude=26.3589,
    longitude=127.7681,
    weapon_stock={
        "F-35B": [make_f35b() for _ in range(18)],
        "Atago-class Aegis": [make_atago() for _ in range(4)],
    },
    ammo_stock={"LongRangeMissile": 1000},
    ammo_defs={"LongRangeMissile": long_range_missile},
)

# 鹿屋 Anti-Sub Base（鹿児島県大隅半島）
fortress_kanoya = Fortress(
    name="Kanoya Anti-Sub Base",
    latitude=31.3667,
    longitude=130.8500,
    weapon_stock={
        "Oyashio-class Submarine": [make_oyashio() for _ in range(5)],
    },
    ammo_stock={"Torpedo": 250},
    ammo_defs={"Torpedo": torpedo},
)
