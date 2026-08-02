def transition(state, action):
    table={"approve":"APPROVED","reject":"REJECTED","cancel":"CANCELLED"}
    return table[action]
