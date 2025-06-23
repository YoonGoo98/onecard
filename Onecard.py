import random
import os

# ===================== 설정 =====================
# 사용할 무늬(SUIT)와 숫자(RANK), 조커 설정
SUITS = '♥♣♠◆'
RANKS = [str(i) for i in range(2, 11)] + list('JQKA')
JOKERS = [('Joker', 'black'), ('Joker', 'colored')]
# 각 공격 카드에 따른 데미지 값 정의 (수정된 조커 데미지)
DAMAGE_MAP = {'colored': 10, 'black': 7, 'A': 3, '2': 2}
# 플레이어 수 및 초기 카드 수 설정
MAX_PLAYERS = 2
CARDS_PER_PLAYER = 7

# ===================== 초기화 =====================
def create_deck():
    # 전체 덱을 생성
    return [(s, r) for s in SUITS for r in RANKS] + JOKERS

def shuffle_and_distribute(deck, player_count):
    # 덱을 셔플하고 플레이어 수에 따라 손패 분배
    random.shuffle(deck)
    hands = [[deck.pop() for _ in range(CARDS_PER_PLAYER)] for _ in range(player_count)]
    put_pile = [deck.pop()]  # 시작 카드
    return hands, put_pile

# ===================== 카드 관련 함수 =====================
def is_attack_card(card):
    # 공격 카드인지 판단 (A, 2 또는 Joker)
    return card[0] == 'Joker' or card[1] in ['A', '2']

def get_damage(card):
    # 카드에 해당하는 데미지 반환
    return DAMAGE_MAP.get(card[1], 0)

def card_str(card):
    # 카드 튜플을 문자열로 표현
    return f'[{card[0]}{card[1]}]'

def hand_str(hand):
    # 손패를 문자열로 연결해 표현
    return " ".join(map(card_str, hand))

# ===================== 출력 관련 =====================
message_log = []  # 최근 메시지 저장

def print_game_state(hands, current_player, put_pile, is_attack):
    # 화면을 지우고 현재 상태 출력
    os.system('cls' if os.name == 'nt' else 'clear')
    available = get_available_cards(hands[current_player], put_pile[-1], is_attack)
    print(f":: Last Card :: {card_str(put_pile[-1])}")
    print(f":: Player {current_player + 1} Hand :: {hand_str(hands[current_player])}")
    print(f":: Available :: {hand_str(available)}")
    print("-" * 40)
    for msg in message_log[-10:]:
        print(msg)
    print("-" * 40)

def log(msg):
    # 메시지를 로그에 추가
    message_log.append(msg)

# ===================== 게임 로직 =====================
def get_available_cards(hand, last_card, is_attack):
    # 현재 낼 수 있는 카드 목록 계산
    available = []
    if not is_attack and last_card[0] == 'Joker':
        return hand.copy()
    for card in hand:
        if card[0] == 'Joker':
            available.append(card)
        elif card[0] == last_card[0] or card[1] == last_card[1]:
            if is_attack and get_damage(card) < get_damage(last_card):
                continue
            available.append(card)
    return available

def refill_deck_if_needed(deck, put_pile):
    # 덱이 비어 있을 때 즉시 버린 더미 섞기
    if not deck and len(put_pile) > 1:
        last_card = put_pile.pop()
        deck.extend(put_pile)
        random.shuffle(deck)
        put_pile.clear()
        put_pile.append(last_card)
        log("덱이 비어 버린 더미를 섞어 새 덱으로 사용합니다.")

def draw_cards(deck, hand, count, put_pile):
    # 카드를 지정한 수만큼 뽑음 (뽑기 전에 항상 덱 상태 확인)
    refill_deck_if_needed(deck, put_pile)
    for _ in range(count):
        if not deck:
            refill_deck_if_needed(deck, put_pile)
        if not deck:
            log("덱이 비었습니다. 더 이상 카드를 뽑을 수 없습니다.")
            break
        hand.append(deck.pop())

def player_turn(player_idx, hands, put_pile, deck, is_attack, damage):
    # 한 명의 턴 처리
    print_game_state(hands, player_idx, put_pile, is_attack)
    hand = hands[player_idx]
    available = get_available_cards(hand, put_pile[-1], is_attack)

    if available:
        # 낼 수 있는 카드가 있는 경우
        if player_idx == 0:
            # 사용자 직접 입력
            try:
                choice = int(input(f"플레이어 {player_idx+1}, 낼 카드 번호 선택 (1~{len(available)}): ")) - 1
                selected = available[choice]
            except:
                log("잘못된 입력입니다. 무작위 카드 선택!")
                selected = random.choice(available)
        else:
            # 컴퓨터는 무작위로 선택
            selected = random.choice(available)

        hand.remove(selected)
        put_pile.append(selected)
        log(f"Player {player_idx+1} plays {card_str(selected)}")

        # 공격 카드인지 확인 및 데미지 누적
        if is_attack_card(selected):
            damage += get_damage(selected)
            is_attack = True
        else:
            is_attack = False
            damage = 0  # 다음 공격을 위해 0으로 초기화

    else:
        # 낼 수 있는 카드가 없으면 뽑기
        if is_attack:
            log(f"Player {player_idx+1} draws {damage} card(s)!")
            draw_cards(deck, hand, damage, put_pile)
        else:
            log(f"Player {player_idx+1} draws 1 card!")
            draw_cards(deck, hand, 1, put_pile)
        is_attack = False
        damage = 0

    # 승리 조건 확인
    if len(hand) == 0:
        log(f"🎉 Player {player_idx+1} wins!")
        print_game_state(hands, player_idx, put_pile, is_attack)
        return True, is_attack, damage

    return False, is_attack, damage

# ===================== 게임 실행 =====================
def main():
    # 게임 초기화 및 루프 실행
    deck = create_deck()
    hands, put_pile = shuffle_and_distribute(deck, MAX_PLAYERS)
    is_attack = False
    damage = 0

    turn = 0
    while True:
        game_over, is_attack, damage = player_turn(turn % MAX_PLAYERS, hands, put_pile, deck, is_attack, damage)
        if game_over:
            break
        turn += 1

# 메인 함수 호출
if __name__ == '__main__':
    main()
