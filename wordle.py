from collections import defaultdict
from functools import cache
from math import log
from typing import Dict, Iterable, FrozenSet, Set, Tuple
from constants import DISPLAY_TOP_GUESSES, WORD_GRAM
from tqdm import tqdm


class Mask:
    none = 0
    appear = 1
    position = 2


class Wordle:
    def __init__(self, words: Iterable[str], answers: Iterable[str]) -> None:
        self.words = frozenset(words)
        self.answers = frozenset(answers)

    @staticmethod
    @cache
    def mask2hint(mask_list: Tuple[int]) -> int:
        return sum(x * pow(3, i) for i, x in enumerate(mask_list))

    @staticmethod
    @cache
    def calc_hint(guess: str, answer: str) -> int:
        mask_list = [Mask.none] * WORD_GRAM
        used = [False] * WORD_GRAM

        for i, (x, y) in enumerate(zip(guess, answer)):
            if x == y:
                mask_list[i] = Mask.position
                used[i] = True

        for i, x in enumerate(guess):
            if mask_list[i] != Mask.none:
                continue
            for j, y in enumerate(answer):
                if x != y or used[j]:
                    continue
                used[j] = True
                mask_list[i] = Mask.appear

        return Wordle.mask2hint(tuple(mask_list))

    @staticmethod
    @cache
    def split_groups(
        guess: str, possibles: FrozenSet[str]
    ) -> defaultdict[int, Set[str]]:
        groups: defaultdict[int, Set[str]] = defaultdict(set)

        for answer in possibles:
            hint = Wordle.calc_hint(guess, answer)
            groups[hint].add(answer)

        return groups

    @cache
    def calc_scores(
        self, possibles: FrozenSet[str], depth: int = 0, progress_bar: bool = False
    ) -> Dict[str, float]:
        scores: Dict[str, float] = dict()
        if depth == 0:
            return scores

        n = len(possibles)
        for guess in tqdm(self.words) if progress_bar else self.words:
            groups = Wordle.split_groups(guess, possibles)

            sub_score = 0
            for group in groups.values():
                sub_score += max(
                    self.calc_scores(frozenset(group), depth - 1).values(), default=0
                )

            # score = sum(p * -log(p))
            score = sum((log(n) - log(len(g))) * len(g) / n for g in groups.values())
            scores[guess] = score + sub_score

        return scores

    def run(self) -> None:
        possibles = self.answers
        round = 1

        while len(possibles) > 1:
            print(f"\nRound {round}:")

            scores: Dict[str, float] = self.calc_scores(possibles, 1, progress_bar=True)
            # self.calc_scores.cache_clear()

            sorted_guesses = sorted(scores.items(), key=lambda x: (x[1], x[0]), reverse=True)  # type: ignore
            guess = sorted_guesses[0][0]

            print("Top Guesses:")
            for g, s in sorted_guesses[:DISPLAY_TOP_GUESSES]:
                print(f'\t"{g}" => {s:.2}')

            print(f'Please guess: "{guess}"')
            print("Input your hint below with no split: ", end="")

            groups = Wordle.split_groups(guess, possibles)
            mask_list = list(map(int, input()))
            hint = Wordle.mask2hint(tuple(mask_list))

            possibles = frozenset(groups[hint])
            round += 1

        if not possibles:
            print("\nNo possible answers left.")
            return

        answer = tuple(possibles)[0]
        print(f'\nAnswer is: "{answer}"')
