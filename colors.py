import random
from typing import Tuple

colors = [(219, 152, 52), (34, 126, 230), (182, 89, 155),
          (113, 204, 46), (94, 73, 52), (15, 196, 241),
          (60, 76, 231)]


def get_rdcolor() -> Tuple[int, int, int]:
    return random.choice(colors)
