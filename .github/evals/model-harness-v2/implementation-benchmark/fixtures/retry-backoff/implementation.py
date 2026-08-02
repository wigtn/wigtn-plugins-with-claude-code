def retry_delays(attempts, base=1, cap=30):
    return [base * (2 ** i) for i in range(attempts)]
