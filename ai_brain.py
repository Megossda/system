from actions import AttackAction, CastSpellAction, LayOnHandsAction
from spells.level_1 import searing_smite, guiding_bolt


class AIBrain:
    """A base class for character decision-making AI."""

    def choose_actions(self, character, combatants):
        """
        Determines the best action and bonus action for a character to take.
        Returns a dictionary with action, bonus_action, and targets.
        """
        action = AttackAction(character.equipped_weapon)
        bonus_action = None
        target = next((c for c in combatants if c.is_alive and c != character), None)

        return {
            'action': action,
            'bonus_action': bonus_action,
            'action_target': target,
            'bonus_action_target': None
        }


class PaladinAIBrain(AIBrain):
    """Smarter, rule-abiding AI for the Paladin class."""

    def choose_actions(self, character, combatants):
        """
        AI Logic:
        1. Bonus Action: Heal with Lay on Hands if below 50% HP.
        2. Bonus Action: If not healing and not concentrating, cast Searing Smite.
        3. Action: If a bonus action spell was cast, MUST take Attack action.
        4. Action: If no bonus action spell, try to cast Guiding Bolt if slots are available.
        5. Action: If all else fails, default to a weapon attack.
        """
        action = None
        bonus_action = None
        action_target = next((c for c in combatants if c.is_alive and c != character), None)
        bonus_action_target = None

        used_bonus_action_spell = False

        # --- Bonus Action Decision ---
        # Priority 1: Heal if wounded
        if character.hp <= character.max_hp / 2:
            loh_action = next((ba for ba in character.available_bonus_actions if isinstance(ba, LayOnHandsAction)),
                              None)
            if loh_action and character.lay_on_hands_pool > 0:
                bonus_action = loh_action
                bonus_action_target = character

                # Priority 2: Use an offensive bonus action spell
        if not bonus_action and not character.concentrating_on:
            smite_action = next((ba for ba in character.available_bonus_actions if ba.name == "Cast Searing Smite"),
                                None)
            if smite_action and character.spell_slots.get(1, 0) > 0:
                bonus_action = smite_action
                bonus_action_target = action_target
                used_bonus_action_spell = True

        # --- Action Decision ---
        # If we cast a bonus action spell, we can only attack (or cast a cantrip).
        if used_bonus_action_spell:
            action = AttackAction(character.equipped_weapon)
        else:
            # If we have spell slots, consider casting a spell as our main action
            if character.spell_slots.get(1, 0) > 0:
                gb_action = next((a for a in character.available_actions if a.name == "Cast Guiding Bolt"), None)
                if gb_action:
                    action = gb_action

            # If no spell action was chosen, default to a weapon attack
            if not action:
                action = AttackAction(character.equipped_weapon)

        return {
            'action': action,
            'bonus_action': bonus_action,
            'action_target': action_target,
            'bonus_action_target': bonus_action_target
        }


class HobgoblinWarriorAIBrain(AIBrain):
    """AI for the Hobgoblin Warrior to choose between melee and ranged attacks."""

    def choose_actions(self, character, combatants):
        action = None
        target = next((c for c in combatants if c.is_alive and c != character), None)

        if target:
            distance = abs(character.position - target.position)
            # If target is far away, use the longbow
            if distance > 5 and character.secondary_weapon:
                action = AttackAction(character.secondary_weapon)
            # Otherwise, use the longsword
            else:
                action = AttackAction(character.equipped_weapon)
        else:
            action = AttackAction(character.equipped_weapon)

        return {'action': action, 'bonus_action': None, 'action_target': target}
