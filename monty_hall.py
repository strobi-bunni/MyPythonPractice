"""
'몬티 홀 문제'(Monty Hall Problem)는 유명한 확률 문제이다.

당신은 한 게임 쇼에 참가했다. 당신 앞에는 세 개의 문이 있으며, 그 중 한 문 뒤에는 경품이 있으며
만약 당신이 경품이 있는 문을 연다면 당신은 경품을 획득한다.

당신이 문을 선택했을 때 사회자는 경품이 없는 다른 문 하나를 열어 보여준다. 이 후 당신에게 문을 바꿀 기회를 준다.
문을 바꾸는 게 유리할까? 아니면 바꾸지 않는 게 유리할까? 아니면 바꾸든지 말든지 차이가 없는가?
그리고 만약 문을 바꾸는(혹은 바꾸지 않는) 게 유리하다고 할 경우 그 확률은?
"""
import random

doors = [1, 2, 3]  # 각각의 문 번호

tries = 10000  # 총 시도할 게임
win_if_changed = 0  # 바꿨을 때 이긴 횟수
win_if_not_changed = 0  # 안바꿨을 때 이긴 횟수

for _ in range(tries):
    prize = random.choice(doors)  # 경품이 있는 문 번호
    your_choice = random.choice(doors)  # 당신이 문을 고른다.

    # 사회자는 경품이 없는 문을 열어 준다.
    halls_choice = random.choice([d for d in doors if d != your_choice and d != prize])

    # 당신은 문을 바꿀 수 있다.
    # 만약 바꾸지 않는다면:
    if your_choice == prize:
        win_if_not_changed += 1

    # 만약 바꾼다면:
    your_choice_changed = [d for d in doors if d != your_choice and d != halls_choice][0]
    if your_choice_changed == prize:
        win_if_changed += 1

print(f"Win if changed: {win_if_changed / tries:.2%}")
print(f"Win if not changed: {win_if_not_changed / tries:.2%}")
