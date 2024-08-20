import tkinter as tk
import random
import time
from pred_engine import PredictionEngine

root = tk.Tk()
root.title("Rock-Paper-Scissors")
root.geometry("500x500")

keybindings = {'rock': None, 'paper': None, 'scissors': None}
binding_step = 0
player_score = 0
computer_score = 0
last_play_time = 0
power_level = 0
engine = PredictionEngine()
rockpaperscissor = ['rock', 'paper', 'scissors']
computer_choice = rockpaperscissor[random.randint(0, 2)]



# Function to set keybindings
def set_keybinding(event):
    global binding_step
    key = event.keysym.lower()
    if binding_step == 0:
        keybindings['rock'] = key
        instruction_label.config(text="Press a key for Paper")
    elif binding_step == 1:
        keybindings['paper'] = key
        instruction_label.config(text="Press a key for Scissors")
    elif binding_step == 2:
        keybindings['scissors'] = key
        instruction_label.config(text=f"Press '{keybindings['rock'].upper()}' for Rock, '{keybindings['paper'].upper()}' for Paper, or '{keybindings['scissors'].upper()}' for Scissors")
        root.bind('<Key>', on_key_press)
    update_power_bar()
    binding_step += 1



def play(user_choice):
    global player_score, computer_score, last_play_time, power_level, computer_choice
    
    
    if user_choice == computer_choice:
        result = "It's a tie!"
    elif (user_choice == 'rock' and computer_choice == 'scissors') or \
         (user_choice == 'paper' and computer_choice == 'rock') or \
         (user_choice == 'scissors' and computer_choice == 'paper'):
        bonus = 1 if power_level > 80 else 0
        result = f"You win!" +  (" Bonus!!" if bonus else "")
        player_score += 1 + bonus
    else:
        penalty = 1 if power_level < 10 else 0
        result = f"You lose!" + (" Penalty :(" if penalty else "")
        computer_score += 1

    computer_choice = rockpaperscissor[engine.predict(rockpaperscissor.index(user_choice), rockpaperscissor.index(computer_choice))]#random.choice(choices)
    
    result_label.config(text=f"Your choice: {user_choice}\nComputer's choice: {computer_choice}\nResult: {result}")
    score_label.config(text=f"Player Score: {player_score}    Computer Score: {computer_score}")
    last_play_time = time.time()


# Create a function to handle key presses
def on_key_press(event):
    key = event.keysym.lower()
    if key == keybindings['rock']:
        play('rock')
    elif key == keybindings['paper']:
        play('paper')
    elif key == keybindings['scissors']:
        play('scissors')


# Function to update the power level bar
def update_power_bar():
    global last_play_time, power_level
    if last_play_time > 0.01:
        power_level = int(max(1 - abs(time.time() - last_play_time - 1), 0) * 100)
        canvas.coords(bar, 10, 10, 10 + power_level * 3.8, 50)
        power_label.config(text=f"Power Level: {power_level}%")
    root.after(16, update_power_bar)  # Update every 20ms for smooth animation


# Initial instruction label
instruction_label = tk.Label(root, text="Press a key for Rock", font=("Arial", 14), pady=20)
instruction_label.pack()

# Create the UI components
result_label = tk.Label(root, text="", font=("Arial", 14), pady=20)
result_label.pack()

# Score label
score_label = tk.Label(root, text="Player Score: 0    Computer Score: 0", font=("Arial", 14), pady=20)
score_label.pack()


# Power level label
power_label = tk.Label(root, text="Power Level: 0%", font=("Arial", 14), pady=10)
power_label.pack()


# Canvas for the power level bar
canvas = tk.Canvas(root, width=380, height=60)
canvas.pack()
bar = canvas.create_rectangle(10, 10, 10, 50, fill="green")


# Bind keys to the play function
root.bind('<Key>', set_keybinding)

# Start the Tkinter event loop
root.mainloop()