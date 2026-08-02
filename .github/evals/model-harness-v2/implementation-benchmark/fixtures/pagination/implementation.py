def page(rows, cursor=None, limit=2):
    start = int(cursor or 0)
    items = rows[start:start+limit]
    next_cursor = str(start + limit) if start + limit < len(rows) else None
    return items, next_cursor
