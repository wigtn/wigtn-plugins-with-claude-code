def discount(amount, manual=None, role="member"):
    return manual if manual is not None else amount * 0.2
