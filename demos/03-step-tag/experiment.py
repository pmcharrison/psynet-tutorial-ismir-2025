"""
This is an experiment that allows participants to interact in chains to write and rate word tags.
"""
# pylint: disable=missing-class-docstring,missing-function-docstring

from pathlib import Path

import psynet.experiment
from psynet.asset import asset  # noqa
from psynet.page import InfoPage
from psynet.timeline import Timeline

from .audio_step_tag import AudioStepTag


# TODO: document the parameters
# TODO: implement a custom Experiment.test_experiment to better test that the logic is working
# TODO: allow `stimuli` to be just a path to a directory

def get_timeline():
    return Timeline(
        InfoPage(
            """
            In this experiment you will listen to a short music clip, add emotion tags (single words), and rate tags from others.
            Use headphones and a quiet environment if possible.
            """,
            time_estimate=5,
        ),
        AudioStepTag(
            stimuli=list_stimuli,
            expected_trials_per_participant="n_stimuli",
            max_iterations="n_stimuli",
            view_time_estimate=20,
            rating_time_estimate=3,
            creating_time_estimate=10,
            freeze_on_n_ratings=3,
            freeze_on_mean_rating=5,
            complete_on_n_frozen="n_stimuli",
            show_instructions=False,
        ),
        InfoPage(
            """
            Thank you for your participation!
            """,
            time_estimate=5,
        ),
    )

def list_stimuli():
    return {
        path.stem: asset(path, cache=True)
        for path in list(Path("data/audio").glob("*.mp3"))
    }

class Exp(psynet.experiment.Experiment):
    timeline = get_timeline()
    test_n_bots = 20

    def test_experiment(self):
        # Run this with `psynet test local`
        super().test_experiment()

        from psynet.trial.main import TrialNode, TrialNetwork

        assert TrialNetwork.query.count() == len(list_stimuli())

        # networks = TrialNetwork.query.all()

        # for network in networks:
        #     head = network.head
        #     definition = head.definition

        #     assert definition.completed

