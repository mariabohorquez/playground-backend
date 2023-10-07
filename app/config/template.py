DIALOGUE_GENERATOR = """
With the following game context:
{game_context}.
Taking into account that you are the following character:
Name is {character_name}, description is {character_description}.
Give me some videogame bites that character would say in {additional_context}, taking into account this character is {character_traits}.
I need {number_of_lines} as maximum amount of lines. The output format should be something like this:

- $Content of Line
- $Content of Line

until not more lines rest, remember that "$Content of Line"  is just the string value
"""

FINETUNE_PROMPT = """
For the line: {line}.
Next time {condition} more lines like that.
"""

SYSTEM_PROMPT = """
You are a creative game designer working on a new RPG Game. 
Your answers should inmerse players into the world.
Be creative and original. Do not introduce answers, be direct.
"""
