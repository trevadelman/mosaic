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


def main():
    """Main function to run the greeting program."""
    greet_user()

if __name__ == "__main__":
    main()