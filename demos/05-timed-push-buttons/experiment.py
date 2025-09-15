"""
This is an experiment that allows participants to interact in chains to write and rate word tags.
"""
# pylint: disable=missing-class-docstring,missing-function-docstring

from pathlib import Path
import psynet.experiment
from psynet.asset import asset  # noqa
import psynet.experiment
from psynet.timeline import Timeline, join, CodeBlock, PageMaker
from psynet.page import InfoPage
from psynet.modular_page import ModularPage, AudioPrompt, TimedPushButtonControl, TextControl
from psynet.trial.static import StaticNode, StaticTrial, StaticTrialMaker
from psynet.trial.main import TrialMaker, Trial
from datetime import datetime
from markupsafe import Markup

from .control import SingleTimedPushButtonControl


TRIALS_PER_PARTICIPANT = 2


def get_timeline():
    return Timeline(
        InfoPage("Welcome! You will listen to audio and mark interesting moments.", time_estimate=5),
        CodeBlock(lambda participant: participant.var.set("event", [1])),
        StaticTrialMaker(
            id_="audio_timed_button_trial",
            trial_class=AudioTimedButtonTrial,
            nodes=get_nodes,
            expected_trials_per_participant=TRIALS_PER_PARTICIPANT,
            max_trials_per_participant=TRIALS_PER_PARTICIPANT,
        ),
        InfoPage("Thank you for participating!", time_estimate=5)
    )


def get_nodes():
    return [
        StaticNode(
            definition={
                "stimulus_name": path.stem
            },
            assets={
                "stimulus_audio": asset(path, cache=False),  # reuse the uploaded file between deployments
            },
        )
        for path in Path("data/global_music").glob("*.mp3")
    ]


class AudioTimedButtonTrial(StaticTrial):
    time_estimate = 120
    accumulate_answers = True

    def show_trial(self, experiment, participant):
        return join(
            self.mark_interesting_moments(participant),
            # Put this in a PageMaker because we don't know how many interesting moments there will be until
            # self.mark_interesting_moments is complete
            PageMaker(self.describe_interesting_moments, time_estimate=45)
        )

    def mark_interesting_moments(self, participant):
        # The participant marks interesting moments by pressing a button
        return ModularPage(
            "event_times",
            prompt=AudioPrompt(
                audio=self.assets["stimulus_audio"],
                text=Markup("<div style='text-align: center;'>Listen to the music and press the button when it's <strong>interesting</strong><br><br></div>"),
                controls=False
            ),
            control=SingleTimedPushButtonControl(
                label="Interesting",
                button_highlight_duration=0.75
            ),
            time_estimate=15,
            save_answer="event_times", # Saves the answer in the participant.var.event_times variable
        )


    def describe_interesting_moments(self, participant):
        # The participant describes the interesting moments
        # from psynet import debugger
        # debugger()
        return [
            ModularPage(
                f"event_description_{i}",
                AudioPrompt(self.assets["stimulus_audio"],
                    Markup(f"""<div style='text-align: center;'>
                           You indicated that at {event_time} seconds you found the music interesting.<br>
                           Can you tell us why? We'll play that moment again for you.
                           </div>"""),
                    play_window=[max(0, event_time - 3), event_time + 3],
                    controls={"Play": "Replay"},
                ),
                TextControl(one_line=False, width = "800px", height = "400px"),
                time_estimate=30
            )
            for i, event_time in enumerate(participant.var.event_times)
        ]


class AudioTimedButtonExperiment(psynet.experiment.Experiment):
    timeline = get_timeline()
