from .containers import Prompt
from .sorters import Sorter
from .evaluators import Evaluator

class Experiment():

    def __init__(self, prompt: Prompt, sorter: Sorter, evaluator: Evaluator) -> None:
        self.prompt = prompt
        self.sorter = sorter
        self.evaluator = evaluator


if __name__ == "__main__":  # pragma: no cover
    pass
