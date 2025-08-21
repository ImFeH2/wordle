from wordle import Wordle
import json

with open("./data/words.json", "r") as f:
    words = json.load(f)

with open("./data/answers.json", "r") as f:
    answers = json.load(f)

print(f"{len(words) = }")
print(f"{len(answers) = }")

assert len(answers) == 2309
assert len(words) == 14855

wordle = Wordle(words, answers)
wordle.run()
