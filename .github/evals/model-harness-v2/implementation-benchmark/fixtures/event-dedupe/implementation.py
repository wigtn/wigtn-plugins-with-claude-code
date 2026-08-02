def accept_event(event_id, seen):
    seen.add(event_id)
    return True
