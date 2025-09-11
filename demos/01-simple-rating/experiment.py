"""
This is a simple experiment that allows participants to rate sounds on a scale of 1 to 5.
"""
# pylint: disable=missing-class-docstring,missing-function-docstring

from pathlib import Path
import psynet.experiment
from psynet.asset import asset  # noqa
from psynet.modular_page import (
    AudioPrompt,
    ModularPage,
    RatingScale,
    MultiRatingControl,
)
from psynet.page import InfoPage
from psynet.timeline import Event, Timeline
from psynet.trial.static import StaticNode, StaticTrial, StaticTrialMaker

# TODO: General dashboard cleaning
# TODO: Make AudioContext requesting less intrusive when it needs to happen (e.g. play button)
# TODO: Automatically waiting for the audio to complete before allowing submission
# TODO: Automatically set cache=True for all assets that are available on deployment
# TODO: Don't create static folder with psynet debug local (maybe revisit calling of _create_symlink)
# TODO: Useful error messages if you put your assets in bad place
# TODO: Better 'reward' footer UI
# TODO: Replace list_stimuli with `psynet info` command,
#       which shows various useful things about the experiment:
# - each trial maker: label, expected number of trials per participant
# - ...


def get_timeline():
    return Timeline(
        InfoPage(
            """
            In this experiment you will hear some sounds. Your task will be to rate
            them on a scale of 1 to 5 on several scales.
            """,
            time_estimate=5,
        ),
        StaticTrialMaker(
            id_="ratings",
            trial_class=CustomTrial,
            nodes=get_nodes,
            expected_trials_per_participant="n_nodes",
        ),
        InfoPage(
            """
            Thank you for your participation!
            """,
            time_estimate=5,
        ),
    )

class CustomTrial(StaticTrial):
    time_estimate = 10

    def show_trial(self, experiment, participant):
        return ModularPage(
            "ratings",
            AudioPrompt(
                self.assets["stimulus_audio"],
                "Please rate the sound. You can replay it as many times as you like.",
                controls="Play",
            ),
            MultiRatingControl(
                RatingScale(
                    name="brightness",
                    values=5,
                    title="Brightness",
                    min_description="Dark",
                    max_description="Bright",
                ),
                RatingScale(
                    name="roughness",
                    values=5,
                    title="Roughness",
                    min_description="Smooth",
                    max_description="Rough",
                ),
            ),
            events={
                "submitEnable": Event(is_triggered_by="promptEnd"),
            },
        )

def get_nodes():
    return [
        StaticNode(
            definition={
                "stimulus_name": path.stem
            },
            assets={
                "stimulus_audio": asset(path, cache=True),  # reuse the uploaded file between deployments
            },
        )
        for path in Path("data/instrument_sounds").glob("*.mp3")
    ]


class Exp(psynet.experiment.Experiment):
    timeline = get_timeline()
