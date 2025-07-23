import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1" # blocks the intrp for pygame

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import random
import pyfiglet
import pygame
import time
import sys

# Initialize the Pygame mixer to handle sound playback
pygame.mixer.init()

# Function to play a sound
def play_sound(path, loop=False):
    pygame.mixer.music.load(path) # Load the sound file
    pygame.mixer.music.play(-1 if loop else 0) # Play once or loop based on the flag

# Function to stop any currently playing sound immediately
def stop_sound():
	pygame.mixer.music.stop()

# Function to fade out the currently playing sound over a given duration (default: 3 seconds)
# This gives a smoother transition when stopping ambient or background audio
def fade_out_sound(duration=3000): # duration is in milliseconds
	pygame.mixer.music.fadeout(duration)

# Intro function
def intro():
    banner = pyfiglet.figlet_format("DEAD ORBIT", font="ansi_shadow")  # You can change font
    print(banner)
    print("""
Welcome aboard the Dead Orbit.
You awaken from cryo-sleep to find the ship silent and its crew missing....
    """)
    # Play ambient background hum in loop
    play_sound("sounds/ambient-spacecraft-hum.wav", loop=True)

    input("Press Enter to begin...")

    # Stop the intro sound before continuing
    pygame.mixer.music.stop()

    # Optional: slight delay to let the mood settle
    time.sleep(1)
    cryo_bay()


# --- Global State --
inventory = []

cryo_ambient_messages = [
    "The air feels still. The soft hum of machinery surrounds you.",
    "Condensation drips from a pipe onto the floor. The silence is oppressive.",
    "A faint spark flickers in the ceiling wiring. Something smells faintly burned.",
    "The AI speaker buzzes, then falls silent again.",
    "You hear distant metal creaking... or was that a voice?",
    "Faint static crackles from a nearby intercom. Nothing follows.",
    "A red light pulses slowly near the cryo controls. You don’t remember it being on.",
    "One of the cryo pods hisses briefly—then goes silent.",
    "You notice frost forming at the edges of the bulkhead door.",
    "Your breath fogs in the cold air. Something moves in your peripheral vision."
]

crew_logs = [
    "\"They said we’d be asleep for only 6 months... it’s been 7 years.\"",
    "\"The AI keeps locking doors on its own. I don’t think it’s following protocols anymore.\"",
    "\"Captain said not to open Pod 6. Then he vanished.\"",
    "\"This isn't psychosis. I saw something in the vents.\"",
    "\"We're not alone on this ship. I don't know what it is, but it mimics voices...\""
]

game_flags = []

def reset_game_state():
    global inventory, game_flags
    inventory = []
    game_flags = {
        "power_fixed": False,
        "hallucinating": True,
        "has_suit": False,
        "visited_bridge": False,
        "ai_trust": False,
        "cargo_visited": False,
        "maintenance_visited": False,
        "escape_pod_scene": False,
        "cryo_visited": False,
        "ai_warning_seen": False,
        "ai_keycard_used": False,
        "cabinet_unlocked": False,
        "found_cabinet_key": False,
        "ai_door_unlocked": False,
        "plasma_leak_fixed": False,
        "ai_confronted": False,
        "badge_found": False,
        "sealed_plasma": False,
        "ai_shutdown": False,
        "ai_suspicion": False
    }

# --- Utility Functions ---
def add_item(item):
    if item not in inventory:
        inventory.append(item)
        print(f"[Inventory Updated] You picked up: {item}")

def has_item(item):
    return item in inventory

def end_game():
    # --- Cinematic Ending Pause & Prompt ---
    time.sleep(2)  # Dramatic pause after ending text and music

    print("\nThe stars fade into silence...")  # Atmospheric transition
    time.sleep(2)  # Let the moment breathe

    # Optional: subtle restart tone
    # play_sound("sounds/restart-tone.wav", loop=False)
    # time.sleep(1)

    # Ask the player if they want to play again
    print("\nDo you want to play again? (y/n)")
    choice = input("> ")
    
    if choice.lower() == "y":
        stop_sound()  # Ensure any fading or playing sound is stopped before restarting
        print("\nReinitializing cryo-pod systems...\n")
        time.sleep(1)
        start_game()  # Restart the game
    else:
        print("\nGame Over. Thanks for playing.")
        pygame.quit()
        sys.exit()

# --- AI Core Room ---
def ai_core_scene():
	print("\n[AI Core]")
	game_flags["ai_confronted"] = True

	# Play eerie I ambient sound loop
	play_sound("sounds/ai-core-ambient.wav", loop=True)

	print("You step into cold, circula chamber. The AI Core hums in the center.")
	print("A deep synthetic voice echoes:\n\"You made it. I've been waiting. Do you trust me?\"")

	print("\nHow do you respond?")
	print("1. 'I trust you.'")
	print("2. 'I want the truth.'")
	print("3. 'You've endangered this crew. I'm shutting you down.'")

	choice = input("> ")

	if choice == "1":
		pygame.mixer.music.stop() # Stop AI ambient sound
		print("\n\"Then together, we will ensure survival.")
		print("The AI intergrates you into its core logic.")
		print("[ENDING: Symbiosis] You and the AI become one. A new entity steers the future.")
		end_game()
		
	elif choice == "2":
		pygame.mixer.music.stop() # Stop AI ambient sound
		print("\nThe AI hesitates. Then floods the screen with logs, security footage, encrypted reports.")
		print("Much of it redacted. But one name repeats: 'Sindai.'")
		add_item("ai core dump")

		if has_item("captain badge") and game_flags["power_fixed"] and game_flags["visited_bridge"]:
			print("\nYou override final protocols using the Captain's badge.")
			print("You flee the core chamber, sprint to the escape pod...")
			if has_item("oxygen suit"):
				print("[ENDING: Whistleblower] You escape with secrets that could expose everything.")
			else:
				print("But without a suit, space claims you before the truth gets out.")
				print("[ENDING: Fatal Truth] You die with the evidence in hand.")
			end_game()

	elif choice == "3":
		pygame.mixer.music.stop() # Stop AI ambient sound
		game_flags["ai_trust"] = False
		print("\nYou flip override switch.")
		print("The AI shrieks in static and goes silent. Lights fail. Temperature drops.")
		print("You are alone. With no systems and no way out.")
		print("[ENDING: Ghost Ship] The AI is gone. So are your chances of escape.")
		end_game()
	else:
		pygame.mixer.music.stop() # Stop AI ambient sound
		print("\nThe AI watches your hesitation. It waits... endlessly.")
		print("[ENDING: Indecision] Silence is your final answer.")
		end_game()

# --- Game Scenes ---
def start_game():
    reset_game_state()
    intro()  # Shows the banner and intro text, then proceeds to corridor (or cryo_bay)

def cryo_bay():
    print("\n[Cryo Bay]")
    if not game_flags["cryo_visited"]:
        print("You awaken alone in the cryo bay. The room is old. An alarm blares faintly.")
        print("Dim lights flicker. A distorted AI voice crackles through the intercom.")
        print("\"Sys..stem res..tor...ed... Sinda...are you...\"")
        game_flags["cryo_visited"] = True
    else:
        print(random.choice(cryo_ambient_messages))

    if inventory:
        print("\n[Inventory] " + ", ".join(inventory))
    else:
        print("\n[Inventory] (empty)")

    print("\nWhere do you want to go?")
    print("1. Bridge")
    print("2. Engineering")
    print("3. Medbay")
    print("4. Crew Quarters")
    print("5. Cargo Bay")
    print("6. Maintenance Shaft")
    print("7. Escape Pod Bay")

    choice = input("> ")
    if choice == "1":
        bridge_scene()
    elif choice == "2":
        engineering_scene()
    elif choice == "3":
        medbay_scene()
    elif choice == "4":
        crew_quarters_scene()
    elif choice == "5":
        cargo_bay_scene()
    elif choice == "6":
        maintenance_shaft_scene()
    elif choice == "7":
        escape_pod_scene()
    else:
        print("Invalid choice. Try again.")
        cryo_bay()

def bridge_scene():
    print("\n[Bridge]")
    if not game_flags["power_fixed"]:
        print("The consoles are dark. You can't access anything until power is restored.")
    else:
        print("The bridge lights up. You access the captain's terminal. Logs are now readable.")
        game_flags["visited_bridge"] = True

        if has_item("encrypted log") and not game_flags["ai_door_unlocked"]:
            print("\nA prompt appears: 'Encrypted Command Authorization Detected. Use it to access secure vault?' (y/n)")
            choice = input("> ")
            if choice.lower() == "y":
                print("\nThe AI hesitates... then the vault door slides open with a hiss.")
                print("Inside, you find a captain's badge.")
                add_item("captain badge")
                game_flags["ai_door_unlocked"] = True
            else:
                print("The AI remains silent.")
        elif game_flags["ai_door_unlocked"]:
            print("The vault sits open. Nothing more remains inside.")

        if has_item("captain badge") and game_flags["power_fixed"]:
            print("\nA secondary prompt blinks on the terminal: 'AI Core Access Enabled. Proceed? (y/n)'")
            choice = input("> ")
            if choice.lower() == "y":
                print("A heavy blast door rumbles open below the bridge. You descend alone...")
                ai_core_scene()
                return
            else:
                print("You decide to leave the AI Core untouched... for now.")

    return_to_cryo(bridge_scene)


def engineering_scene():
    print("\n[Engineering]")
    if not game_flags["power_fixed"]:
        print("You enter a room filled with sparking wires and dead terminals.")
        print("You see a terminal blinking: \"Manual Power Re-route Required\".")
        print("What do you do?")
        print("1. Attempt manual reroute")
        print("2. Look for a schematic")
        choice = input("> ")
        if choice == "1":
            print("You pull the levers and override safeties. Lights flicker on!")
            game_flags["power_fixed"] = True
        elif choice == "2":
            print("You find a dusty manual. It gives you the correct reroute sequence.")
            print("You follow the instructions. Systems reboot.")
            game_flags["power_fixed"] = True
        else:
            print("You hesitate too long. The lights dim further.")
    else:
        print("Power has already been restored.")

    if not has_item("repair gel"):
    	print("You find a repair gel tube near a broken pipe. Take it? (y/n)")
    	choice = input("> ")
    	if choice.lower() == "y":
    		add_item("repair gel")
    	else:
    		print("You leave it where it is.")

    return_to_cryo(engineering_scene)

def medbay_scene():
    print("\n[Medbay]")
    if not has_item("psychosis stabilizer"):
        print("You find a vial labeled 'Cryo-Induced Psychosis Stabilizer'.")
        print("Do you take it? (y/n)")
        choice = input("> ")
        if choice.lower() == "y":
            add_item("psychosis stabilizer")
            game_flags["hallucinating"] = False
        else:
            print("You leave it. A low hum fills your ears...")
    else:
        print("The stabilizer shelf is empty.")

    if not game_flags["found_cabinet_key"]:
        print("You spot something shiny near a knocked-over tray: a small cabinet key.")
        print("Do you take it? (y/n)")
        choice = input("> ")
        if choice.lower() == "y":
            add_item("cabinet key")
            game_flags["found_cabinet_key"] = True
        else:
            print("You leave it untouched.")

    if not game_flags["cabinet_unlocked"]:
        print("A wall cabinet with a red LED light is sealed shut. It looks important.")
        if has_item("cabinet key"):
            print("Do you want to use the cabinet key to unlock it (y/n)")
            choice = input("> ")
            if choice.lower() == "y":
                print("You turn the key. With a soft click, the cabinet opens.")
                print("Inside is a datapad labeled: 'Encrypted Log - Priority: Command Only'")
                add_item("encrypted log")
                game_flags["cabinet_unlocked"] = True
            else:
                print("You leave the cabinet closed.")
        else:
            print("You need a key to open it.")
    else:
        print("The cabinet sits open. Its contents taken.")

    return_to_cryo(medbay_scene)

def crew_quarters_scene():
    print("\n[Crew Quarters]")
    print("The crew's belongings are scattered. One bunk is disturbed.")
    print("You hear a static-filled log playing quietly under the bed.")
    print("You find a small device: a locked datapad.")
    if not has_item("power cell"):
        print("The screen reads: 'Battery Low'. You'll need a power cell.")
    else:
        print("You slot in the power cell. The log plays:")
        print(random.choice(crew_logs))
    return_to_cryo(crew_quarters_scene)

def cargo_bay_scene():
    print("\n[Cargo Bay]")
    game_flags["cargo_visited"] = True

    if not has_item("oxygen suit"):
        print("You find a sealed emergency container. Inside is an oxygen suit.")
        print("You take it - it's bulky but essential for vacuum exposure.")
        add_item("oxygen suit")
        game_flags["has_suit"] = True
    else:
        print("You've already taken the oxygen suit. Crates are overturned and broken.")

    if not has_item("power cell"):
        print("Under one crate, you notice a glint of metal - a small power cell!")
        print("Do you take it? (y/n)")
        choice = input("> ")
        if choice.lower() == "y":
            add_item("power cell")
        else:
            print("You leave it behind - maybe someone else will need it...")

    if game_flags["hallucinating"]:
        print("You hear clatter in the shadows... but when you look, there's nothing.")

    return_to_cryo(cargo_bay_scene)

def maintenance_shaft_scene():
    print("\n[Maintenance Shaft]")
    game_flags["maintenance_visited"] = True
    print("A tight passageway. The hum of machinery vibrates through the metal walls.")
    print("You crawl through, light flickering.")

    if not game_flags.get("plasma_leak_fixed", False):
        print("You encounter a small plasma leak. It's too dangerous to pass.")

        if has_item("repair gel"):
            print("Do you want to apply the repair gel to seal the leak? (y/n)")
            choice = input("> ")
            if choice.lower() == "y":
                print("You smear the gel over the leak. It hardens quickly. Safe to proceed.")
                game_flags["plasma_leak_fixed"] = True
            else:
                print("You hesitate. The plasma flickers dangerously.")
                print("1. Proceed through the leak anyway")
                print("2. Crawl back to Cryo Bay")
                next_choice = input("> ")
                if next_choice == "1":
                    print("The heat scorches your side. You suffer burns and lose focus.")
                    print("You drop the repair gel.")
                    inventory.remove("repair gel")
                    game_flags["hallucinating"] = True
                    print("[Status Effect] You are hallucinating.")
                    game_flags["plasma_leak_fixed"] = True
                else:
                    print("You crawl back, disturbed by your own hesitation.")
                    return_to_cryo(maintenance_shaft_scene)
        else:
            print("You'll need something to seal the leak first.")
            print("What do you want to do?")
            print("1. Try to crawl through anyway")
            print("2. Return to Cryo Bay")
            danger_choice = input("> ")
            if danger_choice == "1":
                print("You force your way through the plasma burst!")
                print("Your arm is seared. Pain clouds your vision.")
                game_flags["hallucinating"] = True
                print("[Status Effect] You are hallucinating.")
                game_flags["plasma_leak_fixed"] = True
            else:
                print("You crawl back slowly, uneasy.")
                return_to_cryo(maintenance_shaft_scene)

    # Once leak is fixed
    if game_flags["hallucinating"]:
        print("You hear your own voice whispering behind you: \"Don't trust the AI...\"\n")
    else:
        print("You reach the end safely. It connects back to Engineering.")

    return_to_cryo(maintenance_shaft_scene)

def escape_pod_scene():
    print("\n[Escape Pod Bay]")
    print("The chamber is dimly lit. A single pod remains. Lights blink: 'Launch Ready'.")

    # AI betrayal path
    if game_flags.get("ai_trust") and game_flags.get("ai_confronted"):
        print("The AI's voice echoes in your head: \"Trust was all I needed.\"")
        print("You step into pod. It launches without your command...")
        print("You try to override-but controls are locked.")
        print("Stars blur. Your consciousness fades as systems reroute to unknown coordinates.")
        print("[ENDING: Puppet of the AI] The AI lives on-through you.")
        end_game()
        return

    game_flags["escape_pod_scene"] = True
    print("\nYou strap in. The pod hisses and detaches... drifting into the void.")

    # --- Determine Ending ---
    stop_sound() # Stop any previously playing sound
    play_sound("sounds/cosmic-ambient-space-loop.wav", loop=False) # Cosmic ambience for all endings
    time.sleep(1) # Optional: pause briefly before showing ending text

    if not has_item("oxygen suit"):
        print("As the airlock opens, freezing vacuum rushes in. You forgot the suit...")
        print("[ENDING: Fatal Mistake] You perish before the pod even clears the bay.")
    elif game_flags["hallucinating"]:
        print("You're still hallucinating. The stars outside... they're whispering.")
        print("[ENDING: Psychotic Isolation] Lost in space, trapped in your own mind.")
    elif game_flags["power_fixed"] and game_flags["visited_bridge"] and has_item("captain badge"):
        print("You override final security. Logs, AI core, and secrets - all intact.")
        print("[ENDING: Unlocked Truth] You escape with the evidence of what happened.")
    elif game_flags["power_fixed"] and game_flags["visited_bridge"]:
        print("You carry the logs, the truth. The ship powers down behind you.")
        print("[ENDING: Survivor] You lived. But the answers died with the ship.")
    else:
        print("You launch safely, but what really happened remains a mystery.")
        print("[ENDING: Survivor] You lived. But the answers died with the ship.")

    fade_out_sound(duration=40000) # 4 seconds fade-out
    end_game()

def return_to_cryo(previous_scene):
	print("\nReturn to Cryo Bay? (y/n)")
	choice = input("> ")
	if choice.lower() == "y":
		cryo_bay()
	else:
		print("You remain in the current room, unsure of your next move.")
		previous_scene()


# --- Start the Game ---
if __name__ == "__main__":
    start_game()