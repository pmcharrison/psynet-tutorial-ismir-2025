import json
import tempfile
import numpy as np

from markupsafe import Markup

from repp.analysis import REPPAnalysis
from repp.config import sms_tapping

from psynet.asset import LocalStorage
from psynet.modular_page import AudioPrompt, AudioRecordControl, ModularPage
from psynet.timeline import ProgressDisplay, ProgressStage
from psynet.trial.audio import AudioRecordTrial
from psynet.trial.static import StaticTrial


class TapTrial(AudioRecordTrial, StaticTrial):
    def get_info(self):
        with tempfile.NamedTemporaryFile() as f:
            self.assets["stimulus"].export_subfile("info.json", f.name)
            with open(f.name, "r") as reader:
                return json.loads(
                    json.load(reader)
                )  # For some reason REPP double-JSON-encodes its output

    def analyze_recording(self, audio_file: str, output_plot: str):
        info = self.get_info()
        stim_name = info["stim_name"]
        title_in_graph = "Participant {}".format(self.participant_id)
        analysis = REPPAnalysis(config=sms_tapping)
        output, analysis, is_failed = analysis.do_analysis(
            info, audio_file, title_in_graph, output_plot
        )
        output = json.dumps(output, cls=NumpySerializer)
        analysis = json.dumps(analysis, cls=NumpySerializer)
        return {
            "failed": is_failed["failed"],
            "reason": is_failed["reason"],
            "output": output,
            "analysis": analysis,
            "stim_name": stim_name,
        }

    def show_trial(self, experiment, participant):
        info = self.get_info()
        duration_rec = info["stim_duration"]
        trial_number = self.position + 1
        return ModularPage(
            "trial_main_page",
            AudioPrompt(
                self.assets["stimulus"].url + "/audio.wav",
                Markup(
                    f"""
                    <br><h3>Tap in time with the metronome.</h3>
                    Trial number {trial_number} out of {self.trial_maker.expected_trials_per_participant}  trials.
                    """
                ),
            ),
            AudioRecordControl(
                duration=duration_rec,
                show_meter=False,
                controls=False,
                auto_advance=False,
                bot_response_media=self.get_bot_response_media(),
            ),
            time_estimate=duration_rec + 5,
            progress_display=ProgressDisplay(
                show_bar=True,  # set to False to hide progress bar in movement
                stages=[
                    ProgressStage(
                        3.5,
                        "Wait in silence...",
                        "red",
                    ),
                    ProgressStage(
                        [3.5, (duration_rec - 6)],
                        "START TAPPING!",
                        "green",
                    ),
                    ProgressStage(
                        3.5,
                        "Stop tapping and wait in silence...",
                        "red",
                        persistent=False,
                    ),
                    ProgressStage(
                        0.5,
                        "Press Next when you are ready to continue...",
                        "orange",
                        persistent=True,
                    ),
                ],
            ),
        )

    def get_bot_response_media(self):
        try:
            bot_audio = self.assets["bot_response"]
        except KeyError as e:
            raise ValueError(
                "To run bots through this experiment, you must provide a bot_responses argument to get_music_stimuli_loader"
            ) from e
        assert isinstance(bot_audio.storage, LocalStorage), "Sorry, this test currently only supports local storage"
        return bot_audio.storage.get_file_system_path(bot_audio.host_path)


class NumpySerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return super().encode(bool(obj))
        else:
            return super().default(obj)
