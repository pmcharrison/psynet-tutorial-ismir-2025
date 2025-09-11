"""
# DEMO: Tapping Experiemnt to Measure Beat Synchronisation
# This experiment investigates rhythmic tapping abilities through two main tasks:
# 1. Isochronous tapping: Participants tap along with regular metronome beats (600ms and 800ms intervals)
# 2. Musical beat synchronisation: Participants tap along with musical excerpts guided by an initial metronome
#
# The experiment includes volume calibration, recording quality checks, and tapping calibration.
# Data is collected using the REPP framework for precise audio analysis of tapping responses.
"""

# TODO: Improve visual sound levels in volume tests (music and tappin)
# TODO: There may be a wierd bug in the plotting/ analysis of tapping (see output analysis plots in dashboard)
# TODO: PsyNet improvement - automatically extracting n_stimuli and stimuli durations instead of hardcoding them


import psynet.experiment
from psynet.timeline import Timeline
from psynet.trial.static import StaticTrialMaker

# custom pre screening tests to make sure REPP works
from .repp_prescreens import (
    REPPMarkersTest,
    REPPTappingCalibration,
    REPPVolumeCalibrationMusic,
)

from .repp_iso import get_isochronous_stimulus, TapTrialISO, iso_tapping_instructions
from .repp_music import get_music_stimuli_loader, TapTrialMusic, music_tapping_instructions


########################################################
# Timeline
########################################################

def get_timeline():
    return Timeline(
        REPPVolumeCalibrationMusic(),  # calibrate volume with music
        REPPMarkersTest(),  # pre-screening filtering participants based on recording test (markers)
        REPPTappingCalibration(),  # calibrate tapping
        iso_tapping_instructions,
        StaticTrialMaker(
            id_="iso_tapping",
            trial_class=TapTrialISO,
            nodes=isochronous_stimuli,
            expected_trials_per_participant="n_nodes",
        ),
        music_tapping_instructions,
        StaticTrialMaker(
            id_="music_tapping",
            trial_class=TapTrialMusic,
            nodes=music_stimuli_loader,
            expected_trials_per_participant="n_nodes",
        )
    )

########################################################
# Global parameters
########################################################

# Set experiment parameters
TapTrialISO.time_estimate = 40
TapTrialMusic.time_estimate = 40

# Criteria for failing a trial
MIN_RAW_TAPS = 50
MAX_RAW_TAPS = 200


########################################################
# Stimuli
########################################################

# In the isochronous task, the paricipant taps along to a steady metronome.
isochronous_stimuli = [
    get_isochronous_stimulus("iso_800ms", [800] * 15, bot_response="data/iso_bot_responses/example_iso_slow_tap.wav"),
    get_isochronous_stimulus("iso_600ms", [600] * 12, bot_response="data/iso_bot_responses/example_iso_fast_tap.wav"),
]

music_stimuli_loader = get_music_stimuli_loader("data/music_stimuli", "data/music_bot_responses")


########################################################
# Experiment
########################################################

class Exp(psynet.experiment.Experiment):
    timeline = get_timeline()
