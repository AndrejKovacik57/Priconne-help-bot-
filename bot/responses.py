import random

def handle_command(command) -> str:
    p_command = command.lower()
    
    match p_command:
        case 'marinbot':
            return "I'm Marin, and I'm working!"
        case 'rolltest':
            return str(random.randint(1, 6))
        case 'help':
            return "I'm currently being created. Help info will come soon!"
        case 'create clan':
            return "temp"
        case _:
            return "No command inputted! See **!marin help**"