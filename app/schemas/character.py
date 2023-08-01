def character_serializer(character) -> dict:
    return {
        "id": str(character["_id"]),
        "name": character["email"],
        "password": character["password"],
    }


def characters_serializer(characters) -> list:
    return [character_serializer(character) for character in characters]
