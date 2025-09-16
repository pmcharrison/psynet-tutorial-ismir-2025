# pylint: disable=missing-class-docstring,missing-function-docstring

import random
import psynet.experiment
from psynet.modular_page import (
    ModularPage,
    PushButtonControl,
    DropdownControl
)
from psynet.page import InfoPage
from psynet.timeline import Timeline, PageMaker, CodeBlock, while_loop, switch, join, conditional, for_loop


def get_timeline():
    return Timeline(
        ModularPage(
            "color",
            "What is your favorite color?",
            PushButtonControl(choices=["red", "green", "blue"]),
            time_estimate=10,
            save_answer="favorite_color",
        ),
        PageMaker(
            lambda participant: InfoPage(
                f"OK, your favorite color is {participant.var.favorite_color}."
            ),
            time_estimate=5,
        ),
        CodeBlock(
            lambda participant: participant.var.set(
                "random_number",
                random.randint(0, 100),
            )
        ),
        PageMaker(
            lambda participant: InfoPage(
                f"Your random number is {participant.var.random_number}",
            ),
            time_estimate=5,
        ),
        ModularPage(
            "choose_page",
            "Which page do you want to see next?",
            PushButtonControl(choices=["page_1", "page_2", "page_3"]),
            save_answer="choose_page",
            time_estimate=5,
        ),
        switch(
            "choose_page",
            lambda participant: participant.var.choose_page,
            {
                "page_1": InfoPage("page_1", time_estimate=5),
                "page_2": InfoPage("page_2", time_estimate=5),
                "page_3": InfoPage("page_3", time_estimate=5),
            }
        ),
        while_loop(
            "my_loop",
            condition=lambda participant: participant.var.get("score", default=0) <= 5,
            logic=join(
                CodeBlock(lambda participant: participant.var.set("score", random.randint(1, 10))),
                conditional(
                    "feedback",
                    condition=lambda participant: participant.var.score <= 5,
                    logic_if_true=PageMaker(
                        lambda participant: InfoPage(
                            f"You scored {participant.var.score}, bad luck."
                        ),
                        time_estimate=5
                    ),
                    logic_if_false=PageMaker(
                        lambda participant: InfoPage(
                            f"You scored {participant.var.score}, well done!",
                        ),
                        time_estimate=5
                    ),
                )
            ),
            expected_repetitions=2,
        ),
        ModularPage(
            "target_number",
            "What number would you like to count up to?",
            DropdownControl([1, 2, 3, 4, 5]),
            time_estimate=5,
            save_answer="target_number",
        ),
        for_loop(
            label="counting",
            iterate_over=lambda participant: list(range(1, participant.var.target_number + 1)),
            logic=lambda x: InfoPage(str(x), time_estimate=5),
            time_estimate_per_iteration=5,
            expected_repetitions=3,
        ),
    )


class Exp(psynet.experiment.Experiment):
    timeline = get_timeline()
