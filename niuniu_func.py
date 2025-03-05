# import package
import itertools
import random
from collections import Counter

# generate deck
def generate_deck():
    # def poker with rank & suit
    suits = ['spade', 'heart', 'diamond', 'club']
    ranks = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    # generate a poker deck
    return [(suit, rank) for suit in suits for rank in ranks]

# get card value
def card_value(card):
    # J, Q, K == 10
    # A == 1
    rank = card[1]
    return 10 if rank in ['J', 'Q', 'K'] else (1 if rank == 'A' else int(rank))

# get card rank
def get_card_rank(card):
    rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                  'J': 11, 'Q': 12, 'K': 13, 'A': 1}
    return rank_order[card[1]]

# get suit rank
def get_suit_rank(card):
    suit_order = {'spade': 4, 'heart': 3, 'diamond': 2, 'club': 1}
    return suit_order[card[0]]

# caculate fix 5 card type
def calculate_niu(cards):
    # compare value rank then suit rank
    cards_value = [card_value(card) for card in cards]

    # sepcial card type
    if all(card[1] in ['J', 'Q', 'K'] for card in cards):
        return '五公'
    if all(v < 5 for v in cards_value) and sum(cards_value) == 10:
        return '五小牛'
    if sum(1 for card in cards if card[1] in ['J', 'Q', 'K']) == 4 and any(card[1] == '10' for card in cards):
        return '四花牛'

    # normal card type
    for combo in itertools.combinations(cards_value, 3):
        if sum(combo) % 10 == 0:
            remaining = [v for v in cards_value if v not in combo][:2]
            if sum(remaining) % 10 == 0:
                return '牛牛'
            else:
                return f'牛{sum(remaining) % 10}'

    # check J, Q, K
    return '有公無牛' if any(card[1] in ['J', 'Q', 'K'] for card in cards) else '無公無牛'

# def simulate card type rate
def simulate_cardtype_rate(hand, num_simulations=500000):
    # generate poker deck
    deck = generate_deck()

    # remove cards already in hand
    for card in hand:
        deck.remove(card)

    results = Counter()
    for _ in range(num_simulations):
        # random choose a card
        remaining_card = random.choice(deck)
        final_hand = hand + [remaining_card]
        # only want to know card type
        card_type = calculate_niu(final_hand)
        results[card_type] += 1

    total = sum(results.values())
    probabilities = {k: v / total for k, v in results.items()}
    sorted_probabilities = dict(sorted(probabilities.items(), key=lambda item: item[1], reverse=True))
    return sorted_probabilities

# only compare the highest card
# return who win
def compare_highest_card(player_hand, banker_hand):
    player_hand_sorted = sorted(player_hand, key=lambda x: (get_card_rank(x), get_suit_rank(x)), reverse=True)
    banker_hand_sorted = sorted(banker_hand, key=lambda x: (get_card_rank(x), get_suit_rank(x)), reverse=True)
    
    player_max_card = player_hand_sorted[0]
    banker_max_card = banker_hand_sorted[0]

    if get_card_rank(player_max_card) > get_card_rank(banker_max_card):
        return "player"
    elif get_card_rank(player_max_card) < get_card_rank(banker_max_card):
        return "banker"
    else:
        if get_suit_rank(player_max_card) > get_suit_rank(banker_max_card):
            return "player"
        else:
            return "banker"
        
# caculate payout
def calculate_payout(player_hand, banker_hand, verbose=True, debug = True):
    # debug of same card
    if debug:
        if len(set(player_hand)) != len(player_hand):
            return "錯誤：玩家手牌有重複的牌！" if verbose else None
        if len(set(banker_hand)) != len(banker_hand):
            return "錯誤：莊家手牌有重複的牌！" if verbose else None
        combined_hand = player_hand + banker_hand
        if len(set(combined_hand)) != len(combined_hand):
            return "錯誤：玩家與莊家有相同的牌！" if verbose else None


    # def hand's rank
    rank_order = {
        '五小牛': 15, '五公': 14, '四花牛': 13, '牛牛': 12, '牛9': 11, '牛8': 10,
        '牛7': 9, '牛6': 8, '牛5': 7, '牛4': 6, '牛3': 5, '牛2': 4, '牛1': 3,
        '有公無牛': 2, '無公無牛': 1
    }

    # def payout of hand
    rank_mult = {
        '五小牛': 6, '五公': 5, '四花牛': 4, '牛牛': 3, '牛9': 2, '牛8': 2,
        '牛7': 2, '牛6': 1, '牛5': 1, '牛4': 1, '牛3': 1, '牛2': 1, '牛1': 1,
        '有公無牛': 1, '無公無牛': 2
    }

    # get player & banker hand
    player_type = calculate_niu(player_hand)
    banker_type = calculate_niu(banker_hand)

    player_rank = rank_order[player_type]
    banker_rank = rank_order[banker_type]
    player_mult = rank_mult[player_type]
    banker_mult = rank_mult[banker_type]

    # compare hand rank
    if player_rank > banker_rank:
        multiplier = player_mult if banker_type != '無公無牛' else player_mult * 2
        return f"玩家贏，賠率為 {multiplier} 倍" if verbose else multiplier
    elif player_rank < banker_rank:
        multiplier = -banker_mult if player_type != '無公無牛' else -banker_mult * 2
        return f"玩家輸，賠率為 {multiplier} 倍" if verbose else multiplier

    # if same hand, compare max card
    player_max_card = max(player_hand, key=lambda x: (get_card_rank(x), get_suit_rank(x)))
    banker_max_card = max(banker_hand, key=lambda x: (get_card_rank(x), get_suit_rank(x)))

    if get_card_rank(player_max_card) > get_card_rank(banker_max_card):
        return f"玩家贏，賠率為 {player_mult} 倍" if verbose else player_mult
    elif get_card_rank(player_max_card) < get_card_rank(banker_max_card):
        return f"玩家輸，賠率為 {-banker_mult} 倍" if verbose else -banker_mult

    # if same card num, compare suit rank
    if get_suit_rank(player_max_card) > get_suit_rank(banker_max_card):
        return f"玩家贏，賠率為 {player_mult} 倍" if verbose else player_mult
    else:
        return f"玩家輸，賠率為 {-banker_mult} 倍" if verbose else -banker_mult

# def how to choose the multiple
def simulate_ev(player_hand, num_simulations=500000):
    # generate deck
    deck = generate_deck()

    # remove player's card
    for card in player_hand:
        deck.remove(card)

    # save the result payout (each multiplier simulated separately)
    total_payout = {multiplier: 0 for multiplier in range(1, 5)}
    simulations_per_multiplier = num_simulations // len(total_payout)
    for multiplier in range(1, 5):
        for _ in range(simulations_per_multiplier):
            remaining_deck = deck.copy()
            
            # random choose a card for the player
            player_fifth_card = random.choice(remaining_deck)
            final_player_hand = player_hand + [player_fifth_card]

            # remove the card we get
            remaining_deck.remove(player_fifth_card)

            # generate three random enemy hands
            enemy_hands = []
            for _ in range(3):
                enemy_hand = random.sample(remaining_deck, 5)
                for card in enemy_hand:
                    remaining_deck.remove(card)
                enemy_hands.append(enemy_hand)

            # calculate payout (bet 1 per game)
            total_game_payout = sum(calculate_payout(final_player_hand, enemy_hand, verbose=False) for enemy_hand in enemy_hands)

            # weighted payout
            total_payout[multiplier] += total_game_payout * multiplier

    # get mean EV
    ev_results = {multiplier: total_payout[multiplier] / simulations_per_multiplier for multiplier in range(1, 5)}

    # get best EV
    best_multiplier = max(ev_results, key=ev_results.get)

    return best_multiplier, ev_results

# calculate ev against banker (both have niu / no niu)
def calculate_ev_against_banker(player_hand, num_simulations=500000, have_niu=True):
    # generate deck
    deck = generate_deck()

    # remove player's card
    for card in player_hand:
        deck.remove(card)

    # save values
    total_payout = {bet: 0 for bet in range(1, 6)}
    simulations_per_bet = num_simulations // len(total_payout)

    for bet in range(1, 6):
        valid_simulations = 0

        while valid_simulations < simulations_per_bet:
            # random take 4 card
            banker_hand = random.sample(deck, 4)
            banker_values = [card_value(card) for card in banker_hand]

            # check whether have niu
            found = False
            for combo in itertools.combinations(banker_values, 3):
                if sum(combo) % 10 == 0:
                    found = True
                    break

            # if need banker have niu but not, or need no niu but have, skip this round
            if found != have_niu:
                continue

            valid_simulations += 1

            # random choice the last card of banker
            remaining_deck = [card for card in deck if card not in banker_hand]
            banker_fifth_card = random.choice(remaining_deck)
            banker_hand.append(banker_fifth_card)

            # random choice the last card of player
            remaining_deck.remove(banker_fifth_card)
            player_fifth_card = random.choice(remaining_deck)
            player_final_hand = player_hand + [player_fifth_card]

            # calculate payout
            payout_result = calculate_payout(player_final_hand, banker_hand, verbose=False)

            # count ev in each bet independently
            total_payout[bet] += payout_result * bet

    # save payout to dict and find the best
    ev_results = {bet: total_payout[bet] / simulations_per_bet for bet in range(1, 6)}
    best_bet = max(ev_results, key=ev_results.get)

    return ev_results, best_bet


