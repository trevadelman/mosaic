import random
import time


def greet_user():
    """Greets the user and prompts for their name."""
    print("Hello! Welcome to the interactive greeting program.")
    
    # Ask the user for their name
    while True:
        name = input("What is your name? ").strip()
        
        # Check if the user entered a name
        if name:
            # Greet the user with their name
            print(f"Nice to meet you, {name}!")
            break
        else:
            print("You didn't enter your name! Please try again.")

    engage_user(name)


def engage_user(name):
    """Engages the user with random questions or statements."""
    responses = [
        f"So, {name}, what do you do for fun?",
        f"{name}, what is your favorite color?",
        f"If you could visit any place in the world, where would it be, {name}?",
        f"What's a hobby or interest of yours, {name}?"
    ]
    print(random.choice(responses))

    # Add a whimsical twist to the conversation
    animal = random.choice(["cat", "dog", "parrot", "dragon"])
    print(f"By the way, if you could have a {animal} as a pet, what would you name it?")
    pet_name = input("Your pet's name: ").strip()
    time.sleep(2)  # Simulate thinking time
    print(f"Wow! A {animal} named {pet_name}! That sounds amazing!")

    # Add an arbitrary fun response about the pet
    silly_action = random.choice(["jumps over the moon", "writes poetry", "plays the piano", "sings opera"])
    print(f"Imagine that your {animal} named {pet_name} {silly_action}! What a talented pet!")

    # Add a simple yes/no follow-up question
    follow_up = input("Would you like to share more about your fantastical pet? (yes/no): ").strip().lower()
    if follow_up == 'yes':
        further_share = input("Great! What would you like to share? ")
        print(f"Thanks for sharing that, {name}! I appreciate it.")
    elif follow_up == 'no':
        print("No worries! It was nice talking to you.")
    else:
        print("I didn't understand that, but thank you for your time!")


def main():
    """Main function to run the greeting program."""
    greet_user()

if __name__ == "__main__":
    main()