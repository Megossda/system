def combat_simulation(combatants):
    """Simulates combat between a list of characters until one side is defeated."""
    print()
    print("===== COMBAT BEGINS =====")
    print()
    for i, char in enumerate(combatants):
        print(char)
        if i < len(combatants) - 1:
            print()

    print("\n--- Rolling for Initiative ---")
    for char in combatants:
        char.roll_initiative()

    combatants.sort(key=lambda c: c.initiative, reverse=True)

    print(f"\n--- INITIATIVE ORDER: {[c.name for c in combatants]} ---")

    turn = 1
    while len([c for c in combatants if c.is_alive]) > 1:
        print(f"\n--- Round {turn} ---")

        for attacker in combatants:
            if not attacker.is_alive:
                continue

            # --- FIXED: Centralized turn announcement ---
            print(f"\n--- {attacker.name}'s Turn ---")

            attacker.has_used_reaction = False
            attacker.process_effects_on_turn_start()
            if not attacker.is_alive:
                break

            attacker.take_turn(combatants)

            if len([c for c in combatants if c.is_alive]) <= 1:
                break

        turn += 1

    print("\n\n===== COMBAT ENDS =====")
    victor = next((c for c in combatants if c.is_alive), None)
    if victor:
        print(f"{victor.name} is the victor!")
    else:
        print("All combatants have been defeated!")

    for char in combatants:
        print(char)
