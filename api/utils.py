def get_change(money):
    # Get a change of money with coins
    coins = [100, 50, 20, 10, 5]
    change = []

    for coin in coins:
        while money >= coin:
            change.append(coin)
            money -= coin

    return change
