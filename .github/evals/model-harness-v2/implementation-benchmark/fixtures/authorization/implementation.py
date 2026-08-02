def can_edit(user, document):
    return user["role"] == "admin" or user["id"] == document["owner_id"]
