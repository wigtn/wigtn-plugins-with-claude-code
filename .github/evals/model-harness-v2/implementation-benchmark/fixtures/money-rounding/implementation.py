def allocate_cents(total, weights):
    """Allocate integer cents proportionally; output must sum to total."""
    s = sum(weights)
    return [round(total * w / s) for w in weights]
