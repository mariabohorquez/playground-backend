DIALOGUE_GENERATOR = """
With the following game context: 
{game_context}.
Taking into account that you are the following character:
Name is {character_name}, description is {character_description}.
Give me some videogame bites that character would say in {additional_context}, taking into account this character is {character_traits}.
Give me {number_of_lines} lines max. Be creative. Lines should be separated by a new line.
"""
