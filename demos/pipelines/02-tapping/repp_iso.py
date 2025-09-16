import json

from markupsafe import Markup

from psynet.asset import asset
from psynet.page import InfoPage
from psynet.trial.static import StaticNode

from repp.config import sms_tapping
from repp.stimulus import REPPStimulus
from repp.utils import save_json_to_file, save_samples_to_file

from .repp_utils import TapTrial, NumpySerializer



iso_tapping_instructions = InfoPage(
    Markup(
        """
        <h3>Instructions: Tapping to rhythm</h3>
        <hr>
        In each trial, you will hear a metronome sound playing at a constant pace.
        <br><br>
        <b><b>Your goal is to tap in time with the rhythm.</b></b> <br><br>
        Remember:
        <li>Start tapping as soon as the metronome starts and continue tapping in each metronome click.</li>
        <li>At the beginning and end of each rhythm, you will hear three consequtive beeps.
        <li><b><b>Do not tap during these beeps, as they signal the beginning and end of each rhythm.
        </b></b></li>
        </ul>
        <br><br>
        Click <b>next</b> to start tapping!
        <hr>
        """
    ),
    time_estimate=10,
)


class TapTrialISO(TapTrial):
    pass


def get_isochronous_stimulus(name, iois, bot_response=None):
    assets = {"stimulus": asset(generate_basic_stimulus, cache=True, is_folder=True)}

    if bot_response is not None:
        assets["bot_response"] = asset(bot_response, cache=True)

    return StaticNode(
        definition={
            "stim_name": name,
            "list_iois": iois,
        },
        assets=assets,
    )


def generate_basic_stimulus(path, stim_name, list_iois):
    stim_prepared, info = create_iso_stim(stim_name, list_iois)
    save_samples_to_file(stim_prepared, path + "/audio.wav", sms_tapping.FS)
    save_json_to_file(info, path + "/info.json")


def create_iso_stim(stim_name, stim_ioi):
    stimulus = REPPStimulus(stim_name, config=sms_tapping)
    stim_onsets = stimulus.make_onsets_from_ioi(stim_ioi)
    stim_prepared, stim_info, _ = stimulus.prepare_stim_from_onsets(stim_onsets)
    info = json.dumps(stim_info, cls=NumpySerializer)
    return stim_prepared, info
