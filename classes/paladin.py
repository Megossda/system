from core import roll_d20, roll, get_ability_modifier
from base_character import Character
from spells.level_1 import searing_smite, cure_wounds, guiding_bolt
from effects import SearingSmiteEffect
from actions import CastSpellAction, LayOnHandsAction
from ai_brain import PaladinAIBrain


class Paladin(Character):
    """A Paladin class with spellcasting and smite abilities."""

    def __init__(self, name, level, hp, stats, weapon, armor=None, shield=None, oath=None, position=0, xp=0):
        save_proficiencies = ['Wisdom', 'Charisma']
        skill_proficiencies = ['Athletics', 'Persuasion']
        weapon_proficiencies = ['Simple', 'Martial']

        super().__init__(name=name, level=level, hp=hp, stats=stats,
                         weapon=weapon, armor=armor, shield=shield,
                         skill_proficiencies=skill_proficiencies,
                         save_proficiencies=save_proficiencies,
                         weapon_proficiencies=weapon_proficiencies,
                         position=position, xp=xp)

        self.spell_slots = {1: self.get_spell_slots_for_level(1)}
        self.prepared_spells = []
        self.active_smites = []
        self.oath = oath
        self.oath_spells = []

        self.spellcasting_ability_name = "CHA"
        self.ai_brain = PaladinAIBrain()

        # Level 1 Features
        self.lay_on_hands_pool = level * 5
        self.available_bonus_actions.append(LayOnHandsAction())

        if self.oath:
            self.oath_spells = self.oath.get_oath_spells(self.level)
            if guiding_bolt in self.oath_spells:
                self.available_actions.append(CastSpellAction(guiding_bolt))

        self.available_bonus_actions.append(CastSpellAction(searing_smite))

    def use_lay_on_hands(self, amount, target):
        """Heals a creature using the Lay on Hands pool."""
        if self.lay_on_hands_pool <= 0:
            print(f"{self.name} tries to use Lay on Hands, but the pool is empty!")
            return

        heal_amount = min(amount, self.lay_on_hands_pool, target.max_hp - target.hp)
        if heal_amount > 0:
            self.lay_on_hands_pool -= heal_amount
            target.hp += heal_amount
            print(f"BONUS ACTION: {self.name} uses Lay on Hands on {target.name}, healing for {heal_amount} HP.")
            print(f"({self.lay_on_hands_pool} HP remaining in the pool)")
        else:
            print(f"BONUS ACTION: {self.name} uses Lay on Hands, but {target.name} is already at full health.")

    def get_spell_slots_for_level(self, spell_level):
        if self.level < 2: return 0
        if spell_level == 1:
            if self.level < 3: return 2
            if self.level < 5: return 3
            return 4
        return 0

    def get_spellcasting_modifier(self):
        return get_ability_modifier(self.stats['cha'])

    def get_spell_save_dc(self):
        return 8 + self.get_proficiency_bonus() + self.get_spellcasting_modifier()

    def prepare_spells(self, spells_to_prepare):
        self.prepared_spells = list(set(spells_to_prepare + self.oath_spells))
        print(f"{self.name} has prepared the following spells: {[s.name for s in self.prepared_spells]}")

    def cast_spell(self, spell, target=None, action_type="ACTION"):
        if spell not in self.prepared_spells:
            return False
        return spell.cast(self, target)

    def attack(self, target, action_type="ACTION", weapon=None, extra_damage_dice=None):
        """Paladin's attack, with detailed logging."""
        if not self.is_alive or not target or not target.is_alive: return

        weapon_to_use = weapon or self.equipped_weapon

        if abs(self.position - target.position) > 5:
            print(
                f"{action_type}: {self.name} tries to attack {target.name} with {weapon_to_use.name}, but is out of range.")
            return

        print(f"{action_type}: {self.name} attacks {target.name} with {weapon_to_use.name} (AC: {target.ac})!")
        attack_roll, _ = roll_d20()
        attack_modifier = self.get_attack_modifier()
        prof_bonus = self.get_proficiency_bonus()
        total_attack = attack_roll + attack_modifier + prof_bonus
        print(f"ATTACK ROLL: {attack_roll} (1d20) +{attack_modifier} (STR) +{prof_bonus} (Prof) = {total_attack}")

        if total_attack >= target.ac or attack_roll == 20:
            is_crit = (attack_roll == 20)
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The attack hits!")

            damage_parts = {}

            weapon_damage = roll(weapon_to_use.damage_dice)
            if is_crit:
                weapon_damage += roll(weapon_to_use.damage_dice)
            damage_parts[f'{weapon_to_use.name} ({weapon_to_use.damage_dice})'] = weapon_damage

            if extra_damage_dice:
                extra_damage = roll(extra_damage_dice)
                if is_crit: extra_damage += roll(extra_damage_dice)
                damage_parts[f'Bonus ({extra_damage_dice})'] = extra_damage

            if searing_smite in self.active_smites:
                searing_dice = '1d6'
                searing_damage = roll(searing_dice)
                if is_crit:
                    searing_damage += roll(searing_dice)
                damage_parts[f'Searing Smite ({searing_dice})'] = searing_damage
                print(f"** The attack is imbued with Searing Smite! **")
                target.active_effects.append(SearingSmiteEffect(self))
                self.active_smites.remove(searing_smite)
                if self.concentrating_on == searing_smite:
                    self.concentrating_on = None

            if self.spell_slots.get(1, 0) > 0:
                self.spell_slots[1] -= 1
                divine_dice = '2d8'
                divine_damage = roll(divine_dice)
                if is_crit:
                    divine_damage += roll(divine_dice)
                damage_parts[f'Divine Smite ({divine_dice})'] = divine_damage
                print(
                    f"** {self.name} uses a level 1 spell slot for DIVINE SMITE! ({self.spell_slots[1]} remaining) **")

            total_damage = sum(damage_parts.values()) + self.get_damage_modifier()
            damage_log = " + ".join([f"{v} [{k}]" for k, v in damage_parts.items()])
            damage_log += f" +{self.get_damage_modifier()} [STR]"

            print(f"{self.name} deals a total of {total_damage} damage. ({damage_log})")
            target.take_damage(total_damage, attacker=self)
        else:
            print("The attack misses.")
