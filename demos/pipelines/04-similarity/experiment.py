"""
In this experiment participants listen to pairs of sounds and rate their similarity on a scale from 1 to 5.
"""

# pylint: disable=missing-class-docstring,missing-function-docstring

from math import comb
from pathlib import Path

import psynet.experiment
from psynet.asset import Asset, asset  # noqa
from psynet.modular_page import ModularPage, RatingControl
from psynet.page import InfoPage
from psynet.participant import Participant
from psynet.timeline import Event, MediaSpec, ProgressDisplay, Timeline
from psynet.trial.static import StaticNode, StaticTrial, StaticTrialMaker


STIMULUS_DIR = "data/instrument_sounds"
STIMULUS_PATTERN = "*.mp3"

# With a large number of stimuli, the number of pairwise combinations becomes very large,
# so we need to limit the number of trials per participant.
N_TRIALS_PER_PARTICIPANT = 10


def get_nodes():
    stimuli = list_stimuli()
    return [
        StaticNode(
            definition={
                "stimulus_a": stimulus_a["name"],
                "stimulus_b": stimulus_b["name"],
            },
        )
        for stimulus_a in stimuli
        for stimulus_b in stimuli
        if stimulus_a["name"] != stimulus_b["name"]
    ]


def get_assets():
    stimuli = list_stimuli()
    return {
        stimulus["name"]: asset(
            stimulus["path"],
            extension=".mp3",
            cache=True,  # reuse the uploaded file between deployments
        )
        for stimulus in stimuli
    }


def list_stimuli():
    return [
        {
            "name": path.stem,
            "path": path,
        }
        for path in sorted(list(Path(STIMULUS_DIR).glob(STIMULUS_PATTERN)))
    ]


# Run `python3 experiment.py` to list the stimuli.
if __name__ == "__main__":
    stimuli = list_stimuli()
    print(f"Found {len(stimuli)} stimuli:")
    for stimulus in stimuli:
        print(f"- {stimulus['name']}")


class CustomTrial(StaticTrial):
    time_estimate = 10

    def show_trial(self, experiment, participant):
        return ModularPage(
            "ratings",
            "Please listen to Sound A and Sound B and rate their similarity on a scale from 1 to 5.",
            RatingControl(
                values=5,
                min_description="Not at all similar",
                max_description="Very similar",
            ),
            time_estimate=10,
            media=MediaSpec(
                audio={
                    "stimulusA": self.trial_maker.assets[self.definition["stimulus_a"]],
                    "stimulusB": self.trial_maker.assets[self.definition["stimulus_b"]],
                }
            ),
            events={
                "playStimulusA": Event(
                    is_triggered_by="trialStart",
                    js="psynet.audio.stimulusA.play();",
                    message="Sound A",
                    message_color="blue",
                ),
                "silence": Event(
                    is_triggered_by="audioFinished: stimulusA",
                    message="",
                ),
                "playStimulusB": Event(
                    is_triggered_by="silence",
                    delay=0.5,
                    js="psynet.audio.stimulusB.play();",
                    message="Sound B",
                    message_color="blue",
                ),
                "responseEnable": Event(
                    is_triggered_by="audioFinished: stimulusB",
                    delay=0.0,
                ),
                "submitEnable": Event(
                    is_triggered_by="responseEnable",
                    delay=0.0,
                ),
            },
            progress_display=ProgressDisplay([], show_bar=False),
        )


class Exp(psynet.experiment.Experiment):
    label = "Subjective rating"

    timeline = Timeline(
        InfoPage(
            """
            In this experiment you will hear some sounds. Your task will be to rate
            them for similarity on a scale of 1 to 5.
            """,
            time_estimate=5,
        ),
        StaticTrialMaker(
            id_="ratings",
            trial_class=CustomTrial,
            nodes=get_nodes,  # this is a callable, it only gets called on the local machine, where the input files are available
            assets=get_assets,  # likewise a callable
            expected_trials_per_participant=N_TRIALS_PER_PARTICIPANT,
            max_trials_per_participant=N_TRIALS_PER_PARTICIPANT,
        ),
        InfoPage("Thank you for your participation!", time_estimate=5),
    )

    def test_experiment(self):
        super().test_experiment()

        assert Participant.query.count() == 1
        assert CustomTrial.query.count() == N_TRIALS_PER_PARTICIPANT
        assert Asset.query.count() == len(list_stimuli())
        assert (
            StaticNode.query.count() == comb(len(list_stimuli()), 2) * 2
        )  # we see each combination twice, once in each order
