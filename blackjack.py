#! /usr/bin/env python

import os
import random
import shelve

class Player:
    def __init__(self, name, chip_amt):
        self.name = name
        self.chips = chip_amt

class Dealer:
    def __init__(self, name, hand_evaluator):
        self.name = name
        self.hand_evaluator = hand_evaluator
        self.table = []
        self.players = []
        self.sitting_out = []
        self.hand = None
        self.deck = []
        # if db.get_player(self.name):
        #     self.dealer = db.get_player(self.name)
        # else:
        #     self.dealer = Player(self.name, 10000)
        #     db.store_player(self.dealer)
        self.dealer = Player(self.name, 10000)
        self.game_on = 0
        self.bstart = 0

    def dealer_is_broke(self):
        if self.dealer.chips == 0:
            return True

    def deal_self(self):
        hand_scores = [h.val for h in self.table]
        if not [x for x in hand_scores if x < 22]:
            # bot has already won the hand
            self.hand.val = self.hand_evaluator.eval_hand(self.hand.cards)
        else:
            self.hand.val = self.hand_evaluator.eval_hand(self.hand.cards)
            while True:
                if self.hand.val > 16:
                    break
                self.hand.cards.append(self.deck.pop(0))
                self.hand.val = self.hand_evaluator.eval_hand(self.hand.cards)


    def show_table(self):
        t = ''
        t += self.hand.player.name + ': '
        t += self.hand.cards[0] + ' ' + 'X  '
        for hand in self.table:
            t += hand.__repr__()
            t += '   '
        return t

    def assess_hands(self):
        bot_score = self.hand.val
        for hand in self.table:
            hand.val = self.hand_evaluator.eval_hand(hand.cards)
            if hand.val == -1:
                hand.player.chips += 3 * hand.bet
                self.hand.player.chips -= 2 * hand.bet
            elif bot_score > 21:
                hand.player.chips += 2 * hand.bet
                self.hand.player.chips -= hand.bet
            elif 21 >= hand.val > bot_score:
                hand.player.chips += 2 * hand.bet
                self.hand.player.chips -= hand.bet
            elif 21 >= hand.val and hand.val == bot_score:
                hand.player.chips += hand.bet
            elif bot_score > hand.val:
                self.hand.player.chips += hand.bet
            elif hand.val > 21:
                self.hand.player.chips += hand.bet

    def new_hand(self):
        self.table = []
        self.deal()

    def remove_broke_players(self):
        for player in self.players:
            if player.chips <= 0:
                player.chips = 100
                self.sit_out(player)

    def clean_up(self):
        # for player in self.sitting_out:
        #     db.store_player(player)
        # for hand in self.table:
        #     db.store_player(hand.player)
        # db.store_player(self.dealer)
        # db.save_db()
        self.table = []
        self.players = []
        self.hand = []
        self.game_on = 0
        self.bstart = 0

    def get_next_up(self):
        return self.table[0]

    def rotate_hands(self):
        if len(self.table) > 1:
            self.table = self.table[1:] + [self.table[0]]

    def player_actons_complete(self):
        if self.table:
            self.table[0].complete = True
            self.rotate_hands()

    def deal(self):
        self._new_deck()
        self._make_hands()
        self._deal_cards()

    def _deal_cards(self):
        for hand in self.table:
            hand.cards.append(self.deck.pop(0))
            hand.cards.append(self.deck.pop(0))
        self.hand.cards.append(self.deck.pop(0))
        self.hand.cards.append(self.deck.pop(0))

    def _make_hands(self):
        for player in self.players:
            self.table.append(Hand(player))
        self.hand = Hand(self.dealer)

    def _new_deck(self):
        ranks = list('23456789TJQKA')
        suits = list('sdhc')
        self.deck = [x+y for x in ranks for y in suits]
        random.shuffle(self.deck)

    def add_player(self, name):
        # if db.get_player(name):
        #     self.players.append(db.get_player(name))
        # else:
        for player in self.sitting_out:
            if player.name == name:
                self.sit_in(player)
                return None
        player = Player(name, 100)
        self.players.append(player)
        #db.store_player(player)

    def sit_out(self, player):
        self.sitting_out.append(player)
        self.players.remove(player)

    def sit_in(self,player):
        self.players.append(player)
        self.sitting_out.remove(player)

    def kill_player(self,name):
        for player in self.players:
            if player.name == name:
                try:
                    self.players.remove(player)
                except:
                    pass
        for player in self.sitting_out:
                try:
                    self.sitting_out.remove(player)
                except:
                    pass

    def is_player(self, name):
        for player in self.players:
            if player.name == name:
                return True

    def is_sitting_out(self,name):
        for player in self.sitting_out:
            if player.name == name:
                return True

    def has_bet(self,name):
        res = True
        for hand in self.table:
            if hand.bet == 0:
                res = False
        return res

    def bet(self,name, amt):
        for hand in self.table:
            if hand.player.name == name:
                hand.bet = amt
                hand.player.chips -= amt
        for hand in self.table:
            print hand.player.name, hand.bet, hand.player.chips

    def all_bets_in(self):
        for hand in self.table:
            if hand.bet == 0:
                return False
        return True

    def hit(self):
        self.table[0].cards.append(self.deck.pop(0))

    def split(self):
        hand = self.table[0]
        if len(hand.cards) == 2 and hand.cards[0][0] == hand.cards[1][0]:
            if len(self.table) > 1:
                rest = self.table[1:]
                new = Hand(hand.player)
                new.cards = [hand.cards[1], self.deck.pop(0)]
                new.bet = hand.bet
                new.player.chips -= new.bet
                hand.cards[1] = self.deck.pop(0)
                self.table = [hand, new] + rest
            else:
                new = Hand(hand.player)
                new.cards = [hand.cards[1], self.deck.pop(0)]
                new.bet = hand.bet
                new.player.chips -= new.bet
                hand.cards[1] = self.deck.pop(0)
                self.table = [hand, new]
            return True

    def double_down(self):
        hand = self.table[0]
        hand.player.chips -= hand.bet
        hand.bet = hand.bet * 2
        hand.cards.append(self.deck.pop(0))

class Hand:
    def __init__(self,player):
        self.player = player
        self.bet = 0
        self.val = -99
        self.cards = []
        self.complete = False

    def __repr__(self):
        t = self.player.name + ': '
        for card in self.cards:
            t += card + ' '
        return t

class HandEvaluator:
    def __init__(self):
        self.card2int = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                         '6': 6, '7': 7, '8':8,  '9':9,  'T':10,
                         'J':10, 'Q':10, 'K':10}

    def eval_hand(self, hand):
        # eval the cards
        ranks = [x[0] for x in hand]
        if self.is_blackjack(ranks[:]):
            return -1
        elif 'A' not in ranks:
            return self.simple_sum(ranks)
        else:
            return self.with_aces(ranks)

    def with_aces(self, hand):
        nonA = self.simple_sum([x[0] for x in hand if x[0] != 'A'])
        num_of_aces = len([x[0] for x in hand if x[0] == 'A'])
        Avals = []
        if num_of_aces == 1:
            Avals = [1, 11]
        elif num_of_aces == 2:
            for i in [1, 11]:
                for j in [1, 11]:
                    Avals.append(sum([i,j]))
        elif num_of_aces == 3:
            for i in [1, 11]:
                for j in [1, 11]:
                    for k in [1,11]:
                        Avals.append(sum([i,j,k]))
        elif num_of_aces == 4:
            for i in [1, 11]:
                for j in [1, 11]:
                    for k in [1,11]:
                        for l in [1,11]:
                            Avals.append(sum([i,j,k,l]))
        nonAplusA = [a + nonA for a in Avals]
        res = 0
        for val in nonAplusA:
            if res < val < 22:
                res = val
        if res == 0:
            return min(nonAplusA)
        else:
            return res

    def simple_sum(self,ranks):
        return sum([self.card2int[r] for r in ranks])

    def is_blackjack(self,ranks):
        if len(ranks) == 2 and 'A' in ranks:
            ranks.remove('A')
            if ranks[0] in list('TJQK'):
                return True

class DataBase():
    def __init__(self):
        self.path = os.getcwd() + '/blackjack.db'
        self.storage = open('blackjack.db')
        self.db = []
        for line in self.storage.readlines():
            self.db.append(line.strip().split(":"))
        self.storage.close()

    def display_self(self):
        """ for debugging """
        for x in self.db:
            print x[0], ": ", int(x[1])

    def save_db(self):
        f = open(self.path,'w')
        for item in self.db:
            f.write(item[0] + ":" + str(item[1]) + "\n")
        f.close()

    def store_player(self,player):
        for p in self.db:
            if p[0] == player.name:
                self.db.remove(p)
                self.db.append([player.name, player.chips])
                return None
        self.db.append([player.name, player.chips])

    def get_player(self, name):
        for p in self.db:
            if p[0] == name:
                if int(p[1]) <= 0:
                    return Player(name, 100)
                else:
                    return Player(name, int(p[1]))
        if name == 'NO_IAM_BOT':
            pl = Player(name, 10000)
            self.db.append([name,10000])
        else:
            pl = Player(name, 100)
            self.db.append([name, 100])
        return pl

    def add_player(self, player):
        """Adds a new player to the database
        """
        self.db.append([player.name, player.chips])

    def remove_player(self, player):
        for p in self.db:
            if p[0] == player.name:
                self.db.remove(p)

#db = DataBase()
dealer = Dealer('NO_IAM_BOT', HandEvaluator())

## Phenny commands and game functions
def move_on(phenny, input, hand):
    hand.complete = True
    dealer.rotate_hands()
    query_next(phenny, input)

def announce_results(phenny, input):
    phenny.say("%s = %d. %s has %d chips remaining." % (dealer.hand.__repr__(), dealer.hand.val, dealer.hand.player.name, dealer.hand.player.chips))
    for hand in dealer.table:
        phenny.say("%s = %d. %s has %d chips remaining." % (hand.__repr__(), hand.val, hand.player.name, hand.player.chips))

def query_next(phenny,input):
    next_up = dealer.get_next_up()
    if next_up.complete:
        dealer.deal_self()
        dealer.assess_hands()
        announce_results(phenny, input)
        dealer.remove_broke_players()
        if dealer.dealer_is_broke():
            phenny.say("I don't believe it! You broke the bank! All hail Blackjack Genius!")
            dealer.clean_up()
            return None
        if len(dealer.players) == 0:
            phenny.say("The Game is Over!")
            dealer.clean_up()
        else:
            dealer.new_hand()
            phenny.say("Next hand! Place your bets!")
    else:
        phenny.say("%s" % dealer.show_table())
        next_up.val = dealer.hand_evaluator.eval_hand(next_up.cards)
        if next_up.val == -1:
            phenny.say("%s has Blackjack!" % input.nick)
            move_on(phenny, input, next_up)
        elif next_up.val > 21:
            phenny.say("%s  *BUST*" % next_up)
            move_on(phenny, input, next_up)
        elif next_up.val <= 21:
            phenny.say("%s. What's it gonna be?" % next_up)
        else:
            phenny.say("Uh oh! We have a problem, NASA. Better fix me before continuing....")

def bj_challenge(phenny,input):
    if dealer.game_on == 1:
        phenny.say("%s, there is an outstanding challenge." % input.nick)
    else:
        dealer.game_on = 1
        dealer.add_player(input.nick)
        phenny.say("%s has started a game of Blackjack!" % input.nick)
        phenny.say(".bjoin! to join the game. When everyone had joined, issue the command '.bstart'")
bj_challenge.commands = ['bj!', 'blackjack!']

def bj_join(phenny, input):
    if dealer.game_on == 1:
        if dealer.is_player(input.nick):
            phenny.say("%s, you are already in the game!" % input.nick)
        elif dealer.is_sitting_out(input.nick):
            phenny.say("%s, you are sitting out. Try .sit_in" % input.nick)
        else:
            dealer.add_player(input.nick)
            phenny.say("%s has joined the game!" % input.nick)
bj_join.commands = ['bjoin!', 'bjoin']

def bj_start(phenny, input):
    if dealer.game_on == 1:
        if dealer.is_player(input.nick):
            dealer.bstart = 1
            dealer.deal()
            phenny.say("Blackjack starts now! Place your bets!")
            for hand in dealer.table:
                phenny.say("%s starts with %d chips" % (hand.player.name, hand.player.chips))
bj_start.commands = ['bstart']

def bj_bet(phenny, input):
    if dealer.bstart == 1:
        binary = False
        if dealer.is_player(input.nick):
            try:
                int(input.group(2))
            except:
                try:
                    int(input.group(2),2)
                    binary = True
                except:
                    phenny.say("%s, there was something defective about your bet. Try again!" % input.nick)
                    return None
            if not dealer.has_bet(input.nick):
                if not binary:
                    dealer.bet(input.nick, int(input.group(2)))
                    phenny.say("%s has bet %s!" % (input.nick, input.group(2)))
                elif binary:
                    dealer.bet(input.nick, int(input.group(2), 2))
                    phenny.say("%s has bet %s!" % (input.nick, input.group(2)))
                else:
                    phenny.say("%s, you appear to have placed a bet already." % input.nick)
                    return None
                if dealer.all_bets_in():
                    query_next(phenny,input)
    else:
        phenny.say("No one has started the game. The command is '.bstart'")
bj_bet.commands = ['bet!', 'bet']
        # else:
        #     slow = [x for x in dealer.table if x.bet == 0]
        #     for hand in slow:
        #         phenny.say("We are still waiting for %s to bet." % x.player.name)


def bj_hit(phenny,input):
    if dealer.game_on:
        hand = dealer.table[0]
        if hand.player.name == input.nick:
            dealer.hit()
            val = dealer.hand_evaluator.eval_hand(hand.cards)
            hand.val = val
            if hand.val > 21:
                phenny.say("%s  *BUST*" % hand.__repr__())
                move_on(phenny, input, hand)
            else:
                query_next(phenny, input)
        else:
            phenny.say("%s, it is not your turn!" % input.nick)
bj_hit.commands = ['hit!', 'hit']

def bj_stay(phenny, input):
    if dealer.game_on == 1:
        if dealer.table[0].player.name == input.nick:
            hand = dealer.get_next_up()
            phenny.say("%s stays. How boring." % input.nick)
            hand.val = dealer.hand_evaluator.eval_hand(hand.cards)
            move_on(phenny, input, hand)
        else:
            phenny.say("%s, it is not your turn!" % input.nick)
bj_stay.commands = ['stay!', 'stay']

def bj_split(phenny, input):
    if dealer.game_on == 1:
        if dealer.table[0].player.name == input.nick:
            if dealer.table[0].bet > dealer.table[0].player.chips:
                phenny.say("%s, you don't have enough chips to do that." % input.nick)
            elif dealer.split():
                phenny.say("%s has split his hand." % input.nick)
                dealer.show_table()
                query_next(phenny, input)
            else:
                phenny.say("Oh, God. %s, you cannot split in your situation. Please try something else." % input.nick)
        else:
            phenny.say("%s, it is not your turn!" % input.nick)
bj_split.commands = ['split!', 'split']

def bj_double_down(phenny, input):
    if dealer.game_on == 1:
        hand = dealer.table[0]
        if hand.bet > hand.player.chips:
            phenny.say("%s, you don't have enough chips to do that." % input.nick)
        elif hand.player.name == input.nick:
            dealer.double_down()
            hand.val = dealer.hand_evaluator.eval_hand(hand.cards)
            phenny.say("%s doubles down!" % input.nick)
            phenny.say("%s" % hand.__repr__())
            move_on(phenny, input, hand)
        else:
            phenny.say("%s, it is not your turn!" % input.nick)
bj_double_down.commands = ['dd!', 'dd']

def bj_sit_out(phenny,input):
    if dealer.game_on == 1:
        for player in dealer.players:
            if player.name == input.nick:
                dealer.sitting_out.append(player)
                dealer.players.remove(player)
                phenny.say("%s, you are sitting out" % input.nick)
                if len(dealer.players) == 0:
                    phenny.say("The Game is Over!")
                    dealer.clean_up()
bj_sit_out.commands = ['sit_out']

def bj_sit_in(phenny,input):
    if dealer.game_on  == 1:
        for player in dealer.sitting_out:
            if player.name == input.nick:
                dealer.players.append(player)
                dealer.sitting_out.remove(player)
                phenny.say("%s, you are sitting in" % input.nick)
bj_sit_in.commands = ['sit_in']

def bj_ranking(phenny,input):
    all = dealer.sitting_out + dealer.players
    for player in all:
        phenny.say("%s:   %d" % (player.name, player.chips))
bj_ranking.commands = ['brank']

if __name__ == '__main__':
    print __doc__.strip()
