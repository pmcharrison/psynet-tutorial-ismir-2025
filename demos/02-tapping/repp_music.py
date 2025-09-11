import json
from os import PathLike
from pathlib import Path
from typing import Optional

from markupsafe import Markup
from psynet.asset import asset, LocalStorage
from psynet.page import InfoPage
from psynet.trial.static import StaticNode

from repp.config import sms_tapping
from repp.stimulus import REPPStimulus
from repp.utils import save_json_to_file, save_samples_to_file

from .repp_utils import TapTrial, NumpySerializer


music_tapping_instructions = InfoPage(
    Markup(
        """
    <h3>Instructions: Tapping to music</h3>
    <hr>
    Now you will listen to music.
    <b><b>Your goal is to tap in time with the beat of the music until the music ends</b></b><br><br>
    <b><b>The metronome: </b></b>We added a metronome to help you find the
        beat of the music. This metronome will gradually fade out, but you need to keep tapping to
        the beat until the music ends.
    <br><br>
    <img style="width:50%; height:35%;" src="/static/images/example_task.png"  alt="example_task">
    <br><br>
    Click <b>next</b> to start tapping to the music!
    <hr>
    """
    ),
    time_estimate=5,
)


class TapTrialMusic(TapTrial):
    pass


def get_music_stimuli_loader(stimuli: PathLike, bot_responses: Optional[PathLike] = None):
    def deferred():
        nonlocal stimuli
        nonlocal bot_responses

        stimuli = Path(stimuli)

        audios = list(stimuli.glob("*.wav"))  # TODO: is mp3 also supported?
        names = [audio.stem for audio in audios]
        texts = [audio.with_suffix(".txt") for audio in audios]

        for text in texts:
            if not text.exists():
                raise FileNotFoundError(f"Onset file {text} not found")

        if bot_responses is not None:
            bot_responses = Path(bot_responses)
            bot_audios = [
                bot_responses / f"{name}.wav"
                for name in names
            ]
            for bot_audio in bot_audios:
                if not bot_audio.exists():
                    raise FileNotFoundError(f"Bot response file {bot_audio} not found")
        else:
            bot_audios = [None for _ in names]

        nodes = []

        for name, audio, text, bot_audio in zip(names, audios, texts, bot_audios):
            definition = {
                "stim_name": name,
                "audio_filename": str(audio),
                "onset_filename": str(text),
            }
            assets = {
                "stimulus": asset(generate_music_stimulus, cache=True, is_folder=True),
            }
            if bot_audio is not None:
                assets["bot_response"] = asset(bot_audio, cache=True)

            nodes.append(StaticNode(definition=definition, assets=assets))

        return nodes

    return deferred


def generate_music_stimulus(path, stim_name, audio_filename, onset_filename):
    stim_prepared, info = create_music_stim(
        stim_name,
        sms_tapping.FS,
        audio_filename,
        onset_filename,
    )
    save_samples_to_file(stim_prepared, path + "/audio.wav", sms_tapping.FS)
    save_json_to_file(info, path + "/info.json")


def create_music_stim(stim_name, fs, audio_filename, onsets_filename):
    stimulus = REPPStimulus(stim_name, config=sms_tapping)
    stim, stim_onsets, onset_is_played = stimulus.load_stimulus_from_files(
        fs, audio_filename, onsets_filename
    )
    stim_prepared, stim_info = stimulus.filter_and_add_markers(
        stim, stim_onsets, onset_is_played
    )
    info = json.dumps(stim_info, cls=NumpySerializer)
    return stim_prepared, info
