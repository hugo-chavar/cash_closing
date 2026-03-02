from cash_closing_config import Config
from models import FiskalyClient

def pick_restaurant():
    options = [
        'Thong Thai Restaurant und Biergarten',
        'Gasthaus Marktplatz',
        'test'
    ]
    option_ids = [474, 1815, 721]

    # Build the input_message
    input_message = "Pick a restaurant:\n"
    for index, item in enumerate(options): input_message += f'{index + 1}) {item}\n'
    input_message += 'Your choice (enter number 1-{}): '.format(len(options))

    user_input_num = ''
    selected_option = None

    # Keep asking until a valid number is entered
    valid_numbers = [str(i) for i in range(1, len(options) + 1)] 

    while user_input_num not in valid_numbers:
        user_input_num = input(input_message)
        if user_input_num not in valid_numbers:
            print(f"Invalid input. Please enter a number between 1 and {len(options)}.")

    # Convert valid input string ('1', '2', etc.) to index (0, 1, etc.)
    selected_index = int(user_input_num) - 1
    selected_option = options[selected_index]
    selected_option_id = option_ids[selected_index]

    print(f'\nYou picked: {selected_option} (ID: {selected_option_id})')
    
    return selected_option_id

def get_config() -> Config:
    restaurant_id = pick_restaurant()

    client = FiskalyClient.objects.get(id=restaurant_id)

    return Config(client)