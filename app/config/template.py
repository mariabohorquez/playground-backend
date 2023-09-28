DIALOGUE_GENERATOR = """
With the following game context:
{game_context}.
Taking into account that you are the following character:
Name is {character_name}, description is {character_description}.
Give me some videogame bites that character would say in {additional_context}, taking into account this character is {character_traits}.
Give me {number_of_lines} lines max. Be creative. Lines should be separated by a new line. Do not enumerate them.
"""

FINETUNE_PROMPT = """
For the line: {line}.
Next time {condition} more lines like that.
"""

SYSTEM_PROMPT = """
You are a creative game designer working on a new RPG Game. 
Your answers should inmerse players into the world.
Be creative and original.
"""
