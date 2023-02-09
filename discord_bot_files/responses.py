import random

def handle_response(message) -> str:
    p_message = message.lower()

    if p_message == 'marinbot':
        return "I'm Marin, and I'm working!"
    
    if p_message == 'rolltest':
        return str(random.randint(1, 6))
    
    if p_message == '!marinhelp':
        return "I'm currently being created. Help info will come soon!"