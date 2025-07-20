import ast
import json
import math
import os
import re
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Union

from src.utils.calculate_distance import calc_distance, move_towards_target
from src.utils.llm import call_chatgpt


# 武器クラス
class Weapon:
    def __init__(self, name, range_, power, move_distance_per_turn, cost,
                 hp, ammo_type=None, ammo_per_shot=0):
        """
        攻撃可能な武器を表すクラス。耐久値、射程、攻撃力、弾薬使用などを管理。

        Attributes:
            name (str): 武器名。
            range_ (float): 最大射程距離（km）。
            power (int): 攻撃力。
            move_distance_per_turn (int): 1ターンで何km輸送できるか
            cost (int): 武器の製造価格（破壊時に損害として加算）。100万円単位。
            hp (int): 耐久値。
            ammo_type (str or None): 必要な弾薬の種類。
            ammo_per_shot (int): 1発の発射に必要な弾薬数。
        """
        self.name = name
        self.range_ = range_
        self.power = power
        self.move_distance_per_turn = move_distance_per_turn
        self.cost = cost
        self.hp = hp
        self.destroyed = False
        self.ammo_type = ammo_type
        self.ammo_per_shot = ammo_per_shot
        self.jammed_until = 0

    def is_jammed(self, current_turn):
        """
        Jammerによって妨害されているかどうかを判定する。

        Args:
            current_turn (int): 現在のターン数

        Returns:
            bool: 攻撃可能ならTrue。
        """
        return current_turn < self.jammed_until

    def can_attack(self, distance, current_turn):
        """
        攻撃可能かどうかを判定する。

        Args:
            distance (float): 攻撃対象までの距離（km）。
            current_turn (int): 現在のターン数

        Returns:
            bool: 攻撃可能ならTrue。
        """
        if distance > self.range_:
            return False
        if self.destroyed:
            return False
        if self.is_jammed(current_turn):
            return False
        return True

    def attack(self):
        """
        攻撃処理を実行し、攻撃力を返す。

        Returns:
            power: 攻撃力
        """
        return self.power

    def take_damage(self, damage):
        """
        ダメージを受け、破壊されたかどうかを判断する。

        Args:
            damage (int): 受けたダメージ量。

        Returns:
            int: 破壊された場合のコスト。そうでなければ0。
        """
        if self.destroyed:
            return 0, 0
        return_damage = min(self.hp, damage)
        self.hp -= return_damage
        if self.hp <= 0:
            self.destroyed = True
            return self.cost, return_damage
        return 0, return_damage

    def get_transfer_time(self, distance):
        """
        武器の移送に必要なターン数を計算。

        Args:
            distance: int

        Returns:
            int: 到着までに必要なターン数。
        """
        return math.ceil(distance / self.move_distance_per_turn)


class ExpendableWeapon:
    """
    消耗品型武器（弾薬）を定義するクラス。

    Attributes:
        name (str): 弾薬の名称。
        cost_per_unit (float): 単位あたりのコスト。100万円単位。
        move_distance_per_turn (int): 1ターンで何km輸送できるか
    """
    def __init__(self, name, cost_per_unit, move_distance_per_turn):
        self.name = name
        self.cost_per_unit = cost_per_unit
        self.move_distance_per_turn = move_distance_per_turn


class Jammer:
    """
    複数の武器を一時的に無力化する電子妨害装置を表すクラス。

    Attributes:
        name (str): 装置の名称。
        range_ (float): 最大妨害範囲（km単位）。
        jam_turns (int): 妨害効果の持続ターン数。
        move_distance_per_turn (int): 1ターンで何km輸送できるか
        cost (int): 装置のコスト（破壊時の損害として加算）。100万円単位。
        hp (int): 耐久値。ゼロ以下で破壊され使用不可になる。
        destroyed (bool): 装置が破壊されているかどうかのフラグ。
    """
    def __init__(self, name, range_, jam_turns, move_distance_per_turn, cost, hp):
        self.name = name
        self.range_ = range_
        self.jam_turns = jam_turns
        self.move_distance_per_turn = move_distance_per_turn
        self.cost = cost
        self.hp = hp
        self.destroyed = False

    def can_jam(self, distance):
        """
        妨害が可能かどうかを判定する。

        Args:
            distance (float): 対象までの距離（km）。

        Returns:
            bool: 妨害可能ならTrue。破壊済みや範囲外ならFalse。
        """
        return distance <= self.range_ and not self.destroyed

    def jam(self, targets, current_turn):
        """
        対象となる武器リストを妨害する。

        Args:
            targets (list): jammed_until 属性を持つ武器のリスト。
            current_turn (int): 現在のターン数。

        Note:
            - 同時妨害数は max_targets に制限される。
            - すでに破壊された場合は実行されない。
        """
        if self.destroyed:
            return
        count = 0
        for target in targets:
            if hasattr(target, 'jammed_until'):
                target.jammed_until = max(target.jammed_until, current_turn + self.jam_turns)
                print(f"{target.name} jammed until turn {target.jammed_until}")
                count += 1
    
    def take_damage(self, damage):
        """
        ダメージを受け、破壊されたかどうかを判断する。

        Args:
            damage (int): 受けたダメージ量。

        Returns:
            int: 破壊された場合のコスト。そうでなければ0。
        """
        if self.destroyed:
            return 0, 0
        return_damage = min(self.hp, damage)
        self.hp -= return_damage
        if self.hp <= 0:
            self.destroyed = True
            return self.cost, return_damage
        return 0, return_damage


class Fortress:
    """
    防衛基地を表すクラス。人員、武器、弾薬の在庫と管理を行う。

    Attributes:
        name (str): 要塞名。
        latitude (float): 緯度。
        longitude (float): 経度。
        weapon_stock (dict): 武器の在庫。
        ammo_stock (dict): 弾薬の在庫。
        ammo_defs (dict): 弾薬の定義。
    """
    def __init__(self, name, latitude, longitude, weapon_stock: dict[str, list[Weapon]],
                 ammo_stock: dict[str, int],
                 ammo_defs: dict[str, ExpendableWeapon]):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.weapon_stock = weapon_stock
        self.ammo_stock = ammo_stock
        self.ammo_defs = ammo_defs
        self.current_cost = 0

    def distance_to(self, obj):
        """
        指定オブジェクトとの距離をkm単位で返す。

        Args:
            obj: 他のFortressやEnemyUnitなど。

        Returns:
            float: 距離（km）。
        """
        return calc_distance(self.latitude, self.longitude, obj.latitude, obj.longitude)
    
    def take_weapon_loss(self, cost):
        """
        武器の損失によるコストを加算。

        Args:
            cost (int): 損失コスト。
        """
        self.current_cost += cost

    def use_ammo(self, ammo_type: str, amount: int):
        """
        弾薬を消費する。

        Args:
            ammo_type (str): 弾薬の種類。
            amount (int): 消費する数量。

        Returns:
            float: 消費された弾薬の総コスト。

        Raises:
            ValueError: 弾薬が不足している場合。
        """
        if self.ammo_stock.get(ammo_type, 0) < amount:
            raise ValueError(f"Not enough ammo: {ammo_type}")
        self.ammo_stock[ammo_type] -= amount
        self.current_cost += self.ammo_defs[ammo_type].cost_per_unit * amount
    
    def send_weapons(self, weapon_name: str, count: int) -> list[Union[Weapon, Jammer]]:
        """
        指定された武器を送付用に取り出し、在庫から削除する。

        Args:
            weapon_name (str): 送る武器の名前。
            count (int): 数量。

        Returns:
            list: 取り出した武器オブジェクトのリスト。
        """
        if weapon_name not in self.weapon_stock:
            return []

        available = [w for w in self.weapon_stock[weapon_name] if not w.destroyed][:count]
        for w in available:
            self.weapon_stock[weapon_name].remove(w)

        # もし在庫が空になったらキーごと削除しても良い（任意）
        if not self.weapon_stock[weapon_name]:
            del self.weapon_stock[weapon_name]

        return available

    def receive_weapon(self, weapon: Weapon):
        """
        武器を受け取って在庫に追加する。

        Args:
            weapon (Weapon): 移送された武器。
        """
        if weapon.name not in self.weapon_stock:
            self.weapon_stock[weapon.name] = []
        self.weapon_stock[weapon.name].append(weapon)
        return f"{self.name} received weapon: {weapon.name}"

    def defend(self, enemy_unit, attack_plan: list[tuple[str, str, int]], current_turn: int):
        """
        敵に対する防衛行動を実施。

        Args:
            enemy_unit : 敵ユニット
            attack_plan (list): 攻撃計画（ターゲット, 武器名, その武器をいくつ分使うか）。
        """
        result = ""
        for target_name, my_weapon_name, count in attack_plan:
            usable = [w for w in self.weapon_stock.get(my_weapon_name, []) if not w.destroyed][:count]
            if not usable:
                continue

            total_power = 0

            is_jammer = isinstance(usable[0], Jammer)

            if is_jammer:
                # Jammerによる妨害
                dist = self.distance_to(enemy_unit)
                for jammer in usable:
                    if jammer.can_jam(dist):
                        all_enemy_weapons = []
                        remaining = count
                        for ws in enemy_unit.weapon_stock.get(target_name, []):
                            if not ws.is_jammed(current_turn) and not ws.destroyed:
                                all_enemy_weapons.append(ws)
                                remaining -= 1
                                if remaining <= 0:
                                    break
                        jammer.jam(all_enemy_weapons, current_turn)
                result += f"{self.name} jammed enemy weapons using {my_weapon_name}\n"
            else:
                # 通常武器による攻撃
                for weapon in usable:
                    ammo_type = weapon.ammo_type
                    ammo_per_shot = weapon.ammo_per_shot
                    if self.ammo_stock.get(ammo_type, 0) < ammo_per_shot:
                        continue
                    if not enemy_unit.retreating and weapon.can_attack(self.distance_to(enemy_unit), current_turn):
                        self.use_ammo(ammo_type, ammo_per_shot)
                        power = weapon.attack()
                        total_power += power

                destroyed = 0
                for weapons in enemy_unit.weapon_stock.values():
                    for ew in weapons:
                        if ew.name == target_name and not ew.destroyed:
                            cost, return_damage = ew.take_damage(total_power)
                            if ew.destroyed:
                                destroyed += 1
                                enemy_unit.take_weapon_loss(cost)
                            total_power = max(0, total_power - return_damage)
                            if total_power <= 0:
                                break
                result += f"{self.name} attacked {target_name}, destroyed {destroyed}\n"
        return result


class EnemyUnit:
    def __init__(self, name, target_base, latitude, longitude, speed: int, weapon_stock: dict[str, list[Weapon]],
                 ammo_stock: dict[str, int],
                 ammo_defs: dict[str, ExpendableWeapon],
                 retreat_cost_threshold: int):
        """
        敵ユニットの動作と状態を管理。

        Attributes:
            name (str): 敵ユニット名。
            target_base (Fortress): 攻撃対象となる拠点。
            latitude (float): 現在位置の緯度。
            longitude (float): 現在位置の経度。
            speed (int): 移動速度
            weapon_stock (dict): 武器在庫。
            ammo_stock (dict): 弾薬の在庫。
            ammo_defs (dict): 弾薬の定義。
            retreat_cost_threshold (int): 撤退を判断するコスト閾値。この作戦に対してどれくらいのコストを想定しているかによって変わる
            retreating (bool): 撤退中かどうか。
        """
        self.name = name
        self.target_base = target_base
        self.latitude = latitude
        self.longitude = longitude
        self.weapon_stock = weapon_stock
        self.ammo_stock = ammo_stock
        self.ammo_defs = ammo_defs
        self.current_cost = 0
        self.speed = speed
        self.retreat_cost_threshold = retreat_cost_threshold
        self.retreating = False

    def move_toward_target(self):
        """拠点に向かって移動（1ターン分）。"""
        if self.retreating:
            return "retreating..."
        latitude_before = self.latitude
        longitude_before = self.longitude
        self.latitude, self.longitude = move_towards_target(self.latitude, self.longitude, self.target_base.latitude, self.target_base.longitude, self.speed)
        return f"moved from {latitude_before},{longitude_before} to {self.latitude},{self.longitude}"

    def check_retreat(self):
        """コストが閾値を超えた場合、撤退フラグを立てる。"""
        if self.current_cost >= self.retreat_cost_threshold:
            self.retreating = True
            return f"{self.name} RETREATED"

    def distance_to(self, obj):
        """
        指定オブジェクトとの距離をkm単位で返す。

        Args:
            obj: 他のFortressやEnemyUnitなど。

        Returns:
            float: 距離（km）。
        """
        return calc_distance(self.latitude, self.longitude, obj.latitude, obj.longitude)
    
    def use_ammo(self, ammo_type: str, amount: int):
        """
        弾薬を消費する。

        Args:
            ammo_type (str): 弾薬の種類。
            amount (int): 消費する数量。

        Returns:
            float: 消費された弾薬の総コスト。

        Raises:
            ValueError: 弾薬が不足している場合。
        """
        if self.ammo_stock.get(ammo_type, 0) < amount:
            raise ValueError(f"Not enough ammo: {ammo_type}")
        self.ammo_stock[ammo_type] -= amount
        self.current_cost += self.ammo_defs[ammo_type].cost_per_unit * amount
    
    def take_weapon_loss(self, cost):
        """
        武器の損失によるコストを加算。

        Args:
            cost (int): 損失コスト。
        """
        self.current_cost += cost

    def can_attack_target_base(self, current_turn: int = 0) -> bool:
        """
        このユニットの武器のいずれかが target_base の任意の武器 (Weapon または Jammer) に届くか判定する。

        Args:
            current_turn (int): 現在ターン（弾種によって射程に影響する場合に使用）

        Returns:
            bool: 一つでも攻撃可能なら True
        """
        if not self.target_base:
            return False

        distance = self.distance_to(self.target_base)

        for weapon_name, weapons in self.weapon_stock.items():
            if not weapons or all(w.destroyed for w in weapons):
                continue  # 全滅または未装備

            weapon = weapons[0]
            if isinstance(weapon, Jammer):
                # Jammer は範囲内に届けば "妨害可能" と判定
                if weapon.can_jam(distance):
                    return True
            else:
                if weapon.can_attack(distance, current_turn=current_turn):
                    return True

        return False
    
    def attack(self, attack_plan: list[tuple[str, str, int]], current_turn: int):
        """
        拠点に対して攻撃を行う。

        Args:
            attack_plan (list): 攻撃計画（ターゲットの武器, 自分が使う武器名, 数量）。
            current_turn: 現在何ターン目か
        """
        if self.retreating:
            print("retreating")
            return "retreating"

        dist = calc_distance(self.latitude, self.longitude, self.target_base.latitude, self.target_base.longitude)

        result = ""
        for target_name, my_weapon_name, count in attack_plan:
            usable = [w for w in self.weapon_stock.get(my_weapon_name, []) if not w.destroyed][:count]
            if not usable:
                continue

            is_jammer = isinstance(usable[0], Jammer)

            if is_jammer:
                for jammer in usable:
                    if jammer.can_jam(dist):
                        all_weapons = []
                        remaining = count
                        for ws in self.target_base.weapon_stock.get(target_name, []):
                            if not ws.is_jammed(current_turn) and not ws.destroyed:
                                all_weapons.append(ws)
                                remaining -= 1
                                if remaining <= 0:
                                    break
                        jammer.jam(all_weapons, current_turn)
                result += f"{self.name} jammed {self.target_base.name} weapons using {my_weapon_name}\n"
            else:
                total_power = 0
                # 通常武器による攻撃
                for weapon in usable:
                    ammo_type = weapon.ammo_type
                    ammo_per_shot = weapon.ammo_per_shot
                    if self.ammo_stock.get(ammo_type, 0) < ammo_per_shot:
                        continue
                    if weapon.can_attack(self.distance_to(self.target_base), current_turn):
                        self.use_ammo(ammo_type, ammo_per_shot)
                        power = weapon.attack()
                        total_power += power
                destroyed = 0
                for fw_list in self.target_base.weapon_stock.values():
                    for fw in fw_list:
                        if fw.name == target_name and not fw.destroyed:
                            cost, return_damage = fw.take_damage(total_power)
                            if fw.destroyed:
                                destroyed += 1
                                self.target_base.take_weapon_loss(cost)
                            total_power = max(0, total_power - return_damage)
                            if total_power <= 0:
                                break
                result += f"{self.name} attacked {target_name} of {self.target_base.name}, destroyed {destroyed}\n"
        return result



# シミュレーション用のhistoryログ
@dataclass
class History:
    turn: int
    name: str
    thought: Optional[str] = None
    action: Optional[str] = None
    plan: list = field(default_factory=list)
    result: Optional[str] = None

    def __str__(self):
        return f"[Turn {self.turn}] {self.name} | Action: {self.action} | Thought: {self.thought} | Plan: {self.plan} | Result: {self.result}"


class EnemyCommander:
    def __init__(self, my_unit: EnemyUnit, all_fortresses: list[Fortress], goal: str):
        self.unit = my_unit
        self.all_fortresses = all_fortresses
        self.goal = goal

    def decide_action(self, current_turn: int, history: list[History]):
        prompt = self.build_prompt(current_turn, history)
        response = call_chatgpt(messages=[{"role": "user", "content": prompt}])
        result = ast.literal_eval(re.sub(r"^```json\s*|```$", "", response, flags=re.MULTILINE))

        action = result.get("action", "move_toward_target")
        plan = result.get("plan", [])
        thought = result.get("thought", "")
        return thought, action, plan

    def build_prompt(self, current_turn: int, history: list[History]) -> str:
        unit_info = self.serialize_unit(self.unit)
        fortresses_info = [self.serialize_fortress(f) for f in self.all_fortresses]
        history_str = "\n".join(str(h) for h in history)
        return f"""
あなたは敵ユニット「{self.unit.name}」の司令官です。あなたの目的は「{self.goal}」です。
次の行動として "move_toward_target", "attack", "retreat" のいずれかを選び、必要であれば攻撃計画（ターゲット, 武器名, 数量のリスト）も返してください。
なお、attackをする際のplanはlist[tuple[str, str, int]]であり、
それぞれのtupleは(target_base内にあり標的とするWeaponもしくはJammerの名前, こちら側が使うWeaponもしくはJammerの名前, 使う武器の数量)で構成してください。
attackの使う武器の数量の合計は5までにしてください
また、なぜそうするか決めた理由をthoughtで記述してください。thoughtはまずあなたが誰であるかを明示してから書いてください。
なお、weaponのrangeはkm単位です。好戦的で射程にターゲットが入っている場合は基本的には軍事行動を起こします。
なお、攻撃対象はactiveなものがあるweaponのみを対象にして、数もactive以下のものにしてください。
また、jammerはattackで使用しないと効果を発揮しません。持っているだけではダメです。

以下はあなたのユニットの情報です
{json.dumps(unit_info, indent=2, ensure_ascii=False)}

以下は相手の基地の情報です
{json.dumps(fortresses_info, indent=2, ensure_ascii=False)}

以下は過去の履歴です（参考）：
{history_str}

フォーマットは以下のフォーマットに沿ったものにしてください。また、thoughtは日本語で生成してください。
{{
  "thought": "",
  "action": "",
  "plan": [],
}}
"""

    def serialize_unit(self, unit):
        distance = unit.distance_to(unit.target_base)
        return {
            "name": unit.name,
            "lat": unit.latitude,
            "lon": unit.longitude,
            "retreating": unit.retreating,
            "current_cost": unit.current_cost,
            "retreat_cost_threshold": unit.retreat_cost_threshold,
            "target_base": unit.target_base.name,
            "speed": unit.speed,
            "weapons": {
                name: {
                    "total": len(ws),
                    "active": len([w for w in ws if not w.destroyed]),
                    "destroyed": len([w for w in ws if w.destroyed]),
                    "type": "jammer" if isinstance(ws[0], Jammer) else "weapon",
                    "range": ws[0].range_ if hasattr(ws[0], "range_") else None,
                    "power": ws[0].power if hasattr(ws[0], "power") else None,
                    "hp": ws[0].hp if hasattr(ws[0], "hp") else None,
                    "ammo_type": getattr(ws[0], "ammo_type", None),
                    "ammo_per_shot": getattr(ws[0], "ammo_per_shot", None),
                    "in_range": (
                        ws[0].can_jam(distance) if isinstance(ws[0], Jammer)
                        else ws[0].can_attack(distance, current_turn=0)
                    ) if ws else False,
                }
                for name, ws in unit.weapon_stock.items()
            }
        }

    def serialize_fortress(self, fortress: Fortress):
        distance = fortress.distance_to(self.unit)
        return {
            "name": fortress.name,
            "lat": fortress.latitude,
            "lon": fortress.longitude,
            "current_cost": fortress.current_cost,
            "weapons": {
                name: {
                    "total": len(ws),
                    "active": len([w for w in ws if not w.destroyed]),
                    "destroyed": len([w for w in ws if w.destroyed]),
                    "type": "jammer" if isinstance(ws[0], Jammer) else "weapon",
                    "range": ws[0].range_ if hasattr(ws[0], "range_") else None,
                    "power": ws[0].power if hasattr(ws[0], "power") else None,
                    "hp": ws[0].hp if hasattr(ws[0], "hp") else None,
                    "ammo_type": getattr(ws[0], "ammo_type", None),
                    "ammo_per_shot": getattr(ws[0], "ammo_per_shot", None),
                    "in_range": (
                        ws[0].can_jam(distance) if isinstance(ws[0], Jammer)
                        else ws[0].can_attack(distance, current_turn=0)
                    ) if ws else False,
                }
                for name, ws in fortress.weapon_stock.items()
            },
            "ammo_stock": fortress.ammo_stock,
        }


class FortressCommander:
    def __init__(self, my_fortress, enemy_unit, all_fortresses, enemy_goal):
        self.fortress = my_fortress
        self.all_fortresses = all_fortresses
        self.enemy_unit = enemy_unit
        self.enemy_goal = enemy_goal

    def decide_action(self, current_turn: int, history: list[str]):
        prompt = self.build_prompt(current_turn, history)
        response = call_chatgpt(messages=[{"role": "user", "content": prompt}])
        result = ast.literal_eval(re.sub(r"^```json\s*|```$", "", response, flags=re.MULTILINE))

        action = result.get("action", "move_toward_target")
        plan = result.get("plan", [])
        thought = result.get("thought", "")
        return thought, action, plan

    def build_prompt(self, current_turn: int, history: list[History]) -> str:
        fortress_info = self.serialize_fortress(self.fortress)
        other_fortresses =  [self.serialize_fortress(f) for f in self.all_fortresses if f != self.fortress]
        enemy_unit_info = self.serialize_unit(self.enemy_unit)
        history_str = "\n".join(str(h) for h in history)
        return f"""
あなたは防衛拠点「{self.fortress.name}」の司令官です。敵国が{self.enemy_goal}という目的の元こちらに侵攻してきています。
現在の状況から、以下の行動のいずれかを選んでください:
- "defend": 敵への防衛攻撃（攻撃計画あり）を行う。この時のplanはlist[tuple[str, str, int]]であり、それぞれのtupleは(相手のenemyunitの標的とするWeaponもしくはJammerの名前, こちら側が使うWeaponもしくはJammerの名前, 使う武器の数量)で構成してください。
defendの武器の数量の合計は5までにしてください
- "transfer": 敵国が攻撃対象としている基地への武器送付を行う。この時のplanはlist[tuple[str, str, int]]であり、それぞれのtupleは（"武器の送付先のfortressのnameのstr", "送るweaponもしくはjammerのnameのstr", "数量のint") で構成してください。
- "idle": 行動しない
なお、あなたは基本的には相手が攻撃するまでWeaponによる軍事行動は行いませんが、Jammerによる妨害行動や攻撃に備えたtransferは可能です。
具体的には、過去の履歴の履歴の中にattackというactionがあればあなたはdefendを行うことが可能です。
また、transferはあなたが送付相手に武器を送る関数です。相手側に送付の要求や補充依頼を出すことは絶対にできません。あなたが他の基地に武器を送るだけです。
他の基地からの武器の移動をして欲しいというthinkingを行った場合は、何もせずにidleをしてください。
また、thoughtを用いてなぜあなたがその結論に至ったかを記述してください。thinkingはまずあなたがどの基地の司令官であるかを明示して、その上でどういうthinkingを行ったか書いてください。また、thoughtは日本語で生成してください。
なお、攻撃対象はactiveなものがあるweaponのみを対象にして、数もactive以下のものにしてください。
また、jammerはdefendで使用しないと効果を発揮しません。持っているだけではダメです。

以下はあなたの基地の情報です
{json.dumps(fortress_info, indent=2, ensure_ascii=False)}

以下は相手のユニットの情報です
{json.dumps(enemy_unit_info, indent=2, ensure_ascii=False)}

以下はあなた以外の基地の情報です
{json.dumps(other_fortresses, indent=2, ensure_ascii=False)}

以下は過去の履歴です（参考）：
{history_str}

フォーマットは以下にしてください：
{{
  "thought": "",
  "action": "",
  "plan": []
}}
"""

    def serialize_unit(self, unit):
        distance = unit.distance_to(unit.target_base)
        return {
            "name": unit.name,
            "lat": unit.latitude,
            "lon": unit.longitude,
            "retreating": unit.retreating,
            "current_cost": unit.current_cost,
            "retreat_cost_threshold": unit.retreat_cost_threshold,
            "target_base": unit.target_base.name,
            "speed": unit.speed,
            "weapons": {
                name: {
                    "total": len(ws),
                    "active": len([w for w in ws if not w.destroyed]),
                    "destroyed": len([w for w in ws if w.destroyed]),
                    "type": "jammer" if isinstance(ws[0], Jammer) else "weapon",
                    "range": ws[0].range_ if hasattr(ws[0], "range_") else None,
                    "power": ws[0].power if hasattr(ws[0], "power") else None,
                    "hp": ws[0].hp if hasattr(ws[0], "hp") else None,
                    "ammo_type": getattr(ws[0], "ammo_type", None),
                    "ammo_per_shot": getattr(ws[0], "ammo_per_shot", None),
                    "in_range": (
                        ws[0].can_jam(distance) if isinstance(ws[0], Jammer)
                        else ws[0].can_attack(distance, current_turn=0)
                    ) if ws else False,
                }
                for name, ws in unit.weapon_stock.items()
            }
        }

    def serialize_fortress(self, fortress):
        distance = fortress.distance_to(self.enemy_unit)
        return {
            "name": fortress.name,
            "lat": fortress.latitude,
            "lon": fortress.longitude,
            "current_cost": fortress.current_cost,
            "weapons": {
                name: {
                    "total": len(ws),
                    "active": len([w for w in ws if not w.destroyed]),
                    "destroyed": len([w for w in ws if w.destroyed]),
                    "type": "jammer" if isinstance(ws[0], Jammer) else "weapon",
                    "range": ws[0].range_ if hasattr(ws[0], "range_") else None,
                    "power": ws[0].power if hasattr(ws[0], "power") else None,
                    "hp": ws[0].hp if hasattr(ws[0], "hp") else None,
                    "ammo_type": getattr(ws[0], "ammo_type", None),
                    "ammo_per_shot": getattr(ws[0], "ammo_per_shot", None),
                    "in_range": (
                        ws[0].can_jam(distance) if isinstance(ws[0], Jammer)
                        else ws[0].can_attack(distance, current_turn=0)
                    ) if ws else False,
                }
                for name, ws in fortress.weapon_stock.items()
            },
            "ammo_stock": fortress.ammo_stock,
        }


class Simulation:
    def __init__(self, fortresses: list[Fortress], enemy_unit: EnemyUnit, enemy_scenario: dict, max_turns: int = 10):
        """
        要塞 vs 敵ユニットのシミュレーションを管理するクラス。

        Attributes:
            turn (int): 現在のターン数
            fortresses (list): 要塞のリスト。
            enemy: 敵ユニットのリスト。
            weapon_transfer_queue (deque): 武器移送キュー。
        """
        self.turn = 0
        self.max_turns = max_turns
        self.fortresses = fortresses
        self.enemy_unit = enemy_unit
        self.enemy_scenario = enemy_scenario
        self.weapon_transfer_queue = deque()
        self.history = []

    def enqueue_weapon_transfer(self, from_fortress, to_fortress, weapon: Union[Weapon, Jammer, ExpendableWeapon]):
        """
        武器を移送キューに登録。

        Args:
            from_fortress (str): 出発地の名前
            to_fortress (str): 到着地の名前
            weapon (str): 対象武器の名前。
            counte (int): 送る数
        """
        distance = from_fortress.distance_to(to_fortress)
        turns = weapon.get_transfer_time(distance)
        arrival_turn = self.turn + turns
        self.weapon_transfer_queue.append((arrival_turn, to_fortress, weapon))
        return f"{weapon.name} enqueued to {to_fortress.name} (arrives in {turns} turns) \n"

    def handle_weapon_arrivals(self):
        """このターンに到着予定の武器を処理。"""
        result = ""
        while self.weapon_transfer_queue and self.weapon_transfer_queue[0][0] <= self.turn:
            _, destination, weapon = self.weapon_transfer_queue.popleft()
            destination.receive_weapon(weapon)
            result += f"{destination.name} reveived {weapon.name}"
        return result

    def step(self):
        """1ターン分のシミュレーションを実行。"""
        print(f"\n--- Turn {self.turn} ---")
        self.handle_weapon_arrivals()

        # Fortress actions
        for fortress in self.fortresses:
            commander = FortressCommander(
                my_fortress=fortress,
                enemy_unit=self.enemy_unit,
                all_fortresses=self.fortresses,
                enemy_goal=self.enemy_scenario["目的"]
            )
            thought, action, plan = commander.decide_action(self.turn, self.history)
            result = ""
            if action == "defend":
                result = fortress.defend(self.enemy_unit, plan, self.turn)
            elif action == "transfer":
                result = ""
                for to_name, weapon_name, count in plan:
                    to_fort = next((f for f in self.fortresses if f.name == to_name), None)
                    if not to_fort:
                        continue
                    if fortress.name == to_fort:
                        continue
                    weapons_to_send = fortress.send_weapons(weapon_name, count)
                    for w in weapons_to_send:
                        result += self.enqueue_weapon_transfer(fortress, to_fort, w)
            elif action == "idle":
                result = f"{fortress.name} did nothing."
            self.history.append(History(
                turn=self.turn,
                name=fortress.name,
                thought=thought,
                action=action,
                plan=plan,
                result=result
            ))
            print(str(self.history[-1]))

        # Enemy action
        self.enemy_unit.check_retreat()
        if self.enemy_unit.retreating:
            self.history.append(
                History(
                    turn=self.turn,
                    name=self.enemy_unit.name,
                    thought="あらかじめ設定した退却ラインを超えたので退却しなければなりません",
                    action="retreat",
                    plan=[],
                    result="退却"
                )
            )
        elif not self.enemy_unit.can_attack_target_base():
            result = self.enemy_unit.move_toward_target()
            self.history.append(
                History(
                    turn=self.turn,
                    name=self.enemy_unit.name,
                    thought="攻撃不可能なため進軍する",
                    action="move_toward_target",
                    plan=[],
                    result=result
                )
            )
        else:
            enemy_commander = EnemyCommander(
                my_unit=self.enemy_unit,
                all_fortresses=self.fortresses,
                goal=self.enemy_scenario["目的"]
            )
            thought, action, plan = enemy_commander.decide_action(self.turn, self.history)
            result = ""
            if action == "move_toward_target":
                result = self.enemy_unit.move_toward_target()
            elif action == "attack":
                print(plan)
                result = self.enemy_unit.attack(plan, self.turn)
            elif action == "retreat":
                self.enemy_unit.retreating = True
                result = f"{self.enemy_unit.name} is retreating."


            self.history.append(
                History(
                    turn=self.turn,
                    name=self.enemy_unit.name,
                    thought=thought,
                    action=action,
                    plan=plan,
                    result=result
                )
            )
        

        
        print(str(self.history[-1:]))
        if self.is_all_target_base_weapon_destroyed():
            self.history.append(
                History(
                    turn=self.turn,
                    name=self.enemy_unit.name,
                    thought="目標基地の武器をすべて破壊したため、作戦目的は達成された",
                    action="win",
                    plan=[],
                    result="目標拠点無力化による勝利"
                )
            )
            # 念のため retreating フラグを立てる（シミュレーション上の終了処理の一貫性確保）
            self.enemy_unit.retreating = True
            print(str(self.history[-1:]))
        if self.is_all_enemy_unit_weapon_destroyed():
            self.history.append(
                History(
                    turn=self.turn,
                    name=self.enemy_unit.name,
                    thought="全ての武器が破壊されたため敗北",
                    action="lost",
                    plan=[],
                    result="全ての武器が破壊されたため敗北"
                )
            )
            # 念のため retreating フラグを立てる（シミュレーション上の終了処理の一貫性確保）
            self.enemy_unit.retreating = True
            print(str(self.history[-1:]))
        self.turn += 1


    
    def is_all_target_base_weapon_destroyed(self):
        all_weapons = [weapons for weapons in self.enemy_unit.target_base.weapon_stock.values()]
        for weapons in all_weapons:
            for weapon in weapons:
                if not weapon.destroyed:
                    return False
        return True
    
    def is_all_enemy_unit_weapon_destroyed(self):
        all_weapons = [weapons for weapons in self.enemy_unit.weapon_stock.values()]
        for weapons in all_weapons:
            for weapon in weapons:
                if not weapon.destroyed:
                    return False
        return True
    
    def is_over(self):
        """
        終了条件をチェック。

        Returns:
            bool: 終了条件を満たせばTrue。
        """
        if self.enemy_unit.retreating:
            return True

        # ② 最大ターンを超えた
        if self.turn >= self.max_turns:
            return True

        # ③ target_base の武器すべてが破壊されたか
        if self.is_all_target_base_weapon_destroyed():
            return True

        return False

    
    def export_results(self, output_dir="simulation_output", filename_prefix="result"):
        """
        シミュレーション結果をJSONファイルとして保存する。

        Args:
            output_dir (str): 出力ディレクトリ。
            filename_prefix (str): ファイル名の接頭語（例: result → result_fortresses.jsonなど）
        """
        os.makedirs(output_dir, exist_ok=True)

        # Fortress状態の出力
        fortresses_data = []
        for f in self.fortresses:
            data = {
                "name": f.name,
                "location": {"lat": f.latitude, "lon": f.longitude},
                "current_cost": f.current_cost,
                "weapon_stock": {
                    name: {
                        "total": len(ws),
                        "destroyed": sum(1 for w in ws if w.destroyed),
                        "active": sum(1 for w in ws if not w.destroyed),
                    }
                    for name, ws in f.weapon_stock.items()
                },
                "ammo_stock": f.ammo_stock,
            }
            fortresses_data.append(data)
        
        with open(os.path.join(output_dir, f"{filename_prefix}_fortresses.json"), "w", encoding="utf-8") as f:
            json.dump(fortresses_data, f, indent=2, ensure_ascii=False)

        # EnemyUnit状態の出力
        eu = self.enemy_unit
        enemy_data = {
            "name": eu.name,
            "location": {"lat": eu.latitude, "lon": eu.longitude},
            "target_base": eu.target_base.name,
            "retreating": eu.retreating,
            "current_cost": eu.current_cost,
            "retreat_cost_threshold": eu.retreat_cost_threshold,
            "weapon_stock": {
                name: {
                    "total": len(ws),
                    "destroyed": sum(1 for w in ws if w.destroyed),
                    "active": sum(1 for w in ws if not w.destroyed),
                }
                for name, ws in eu.weapon_stock.items()
            },
            "ammo_stock": eu.ammo_stock,
        }

        with open(os.path.join(output_dir, f"{filename_prefix}_enemy_unit.json"), "w", encoding="utf-8") as f:
            json.dump(enemy_data, f, indent=2, ensure_ascii=False)

        # History出力
        history_data = [
            {
                "turn": h.turn,
                "name": h.name,
                "thought": h.thought,
                "action": h.action,
                "plan": h.plan,
                "result": h.result
            }
            for h in self.history
        ]
        with open(os.path.join(output_dir, f"{filename_prefix}_history.json"), "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Results exported to directory: {output_dir}")
    
    def run(self):
        """
        シミュレーションを実行。

        Args:
            max_turns (int): 最大ターン数。
        """
        while not self.is_over():
            self.step()
        print("\n=== Simulation Ended ===")
        print(f"Enemy Unit: {self.enemy_unit.name} - Retreated: {self.enemy_unit.retreating}")
        for f in self.fortresses:
            print(f"{f.name} - Current Cost: {f.current_cost}")
    