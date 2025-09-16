import json
import random
from importlib import resources
from os.path import exists as file_exists
from os.path import join as join_path
from random import shuffle
from typing import List, Optional

from markupsafe import Markup

from psynet.trial import Node

from psynet.asset import ExternalAsset
from psynet.modular_page import (
    AudioMeterControl,
    AudioPrompt,
    AudioRecordControl,
    ModularPage,
    PushButtonControl,
)
from psynet.page import InfoPage, wait_while
from psynet.timeline import (
    Module,
    PageMaker,
    ProgressDisplay,
    ProgressStage,
    join,
)
from psynet.trial.audio import AudioRecordTrial
from psynet.trial.static import StaticTrial, StaticTrialMaker
from psynet.utils import get_logger

from .repp_utils import NumpySerializer

logger = get_logger()


class REPPVolumeCalibration(Module):
    def __init__(
        self,
        label,
        materials_url: str = "https://s3.amazonaws.com/repp-materials",
        min_time_on_calibration_page: float = 3.0,
        time_estimate_for_calibration_page: float = 10.0,
    ):
        super().__init__(
            label,
            join(
                self.introduction,
                self.volume_calibration(
                    min_time_on_calibration_page,
                    time_estimate_for_calibration_page,
                ),
            ),
            assets={
                "volume_calibration_audio": self.asset_calibration_audio(materials_url),
                "rules_image": self.asset_rules(materials_url),
            },
        )

    def asset_calibration_audio(self, materials_url):
        raise NotImplementedError

    def asset_rules(self, materials_url):
        return ExternalAsset(url=materials_url + "/REPP-image_rules.png")

    @property
    def introduction(self):
        return PageMaker(
            lambda assets: InfoPage(
                Markup(
                    f"""
                      <h3>Requirements</h3>
                      <hr>
                      <b>Throughout the experiment, it is very important to <b>ONLY</b> use the laptop speakers and be in a silent environment.
                      <br><br>
                      <i>Please do not use headphones, earphones, external speakers, or wireless devices (unplug or deactivate them now)</i>
                      <hr>
                      <img style="width:70%" src="{assets['rules_image'].url}" alt="rules_image">
                      """
                ),
            ),
            time_estimate=5,
        )

    def volume_calibration(
        self,
        min_time_on_calibration_page,
        time_estimate_for_calibration_page,
    ):
        return PageMaker(
            lambda assets: ModularPage(
                "volume_test",
                AudioPrompt(
                    assets["volume_calibration_audio"],
                    self.calibration_instructions,
                    loop=True,
                ),
                self.AudioMeter(min_time=min_time_on_calibration_page, calibrate=False),
            ),
            time_estimate=time_estimate_for_calibration_page,
        )

    class AudioMeter(AudioMeterControl):
        pass

    @property
    def calibration_instructions(self):
        return Markup(
            f"""
            <h3>Volume test</h3>
            <hr>
            <h4>We will begin by calibrating your audio volume:</h4>
            <ol>
                <li>{self.what_are_we_playing}</li>
                <li>Set the volume in your laptop to approximately 90% of the maximum.</li>
                <li><b>The sound meter</b> below indicates whether the audio volume is at the right level.</li>
                <li>If necessary, turn up the volume on your laptop until the sound meter consistently indicates that
                the volume is <b style="color:green;">"just right"</b>.
            </ol>
            <hr>
            """
        )

    @property
    def what_are_we_playing(self):
        return "A sound is playing to help you find the right volume in your laptop speakers."


class REPPVolumeCalibrationMusic(REPPVolumeCalibration):
    """
    This is a volume calibration test to be used when implementing SMS experiments with music stimuli and REPP. It contains
    a page with general technical requirements of REPP and a volume calibration test with a visual sound meter
    and stimulus customized to help participants find the right volume to use REPP.

    Parameters
    ----------
    label : string
        The label for the REPPVolumeCalibration test, default: "repp_volume_calibration_music".

    materials_url: string
        The location of the REPP materials, default: https://s3.amazonaws.com/repp-materials.

    min_time_on_calibration_page : float
        Minimum time (in seconds) that the participant must spend on the calibration page, default: 5.0.

    time_estimate_for_calibration_page : float
        The time estimate for the calibration page, default: 10.0.
    """

    def __init__(
        self,
        label="repp_volume_calibration_music",
        materials_url: str = "https://s3.amazonaws.com/repp-materials",
        min_time_on_calibration_page: float = 5.0,
        time_estimate_for_calibration_page: float = 10.0,
    ):
        super().__init__(
            label,
            materials_url,
            min_time_on_calibration_page,
            time_estimate_for_calibration_page,
        )

    def asset_calibration_audio(self, materials_url):
        return ExternalAsset(
            url=materials_url + "/calibrate.prepared.wav",
        )

    class AudioMeter(AudioMeterControl):
        decay = {"display": 0.1, "high": 0.1, "low": 0.1}
        threshold = {"high": -20, "low": -40}
        grace = {"high": 0.0, "low": 1.5}
        warn_on_clip = True
        msg_duration = {"high": 0.25, "low": 0.25}

    @property
    def what_are_we_playing(self):
        return "A music clip is playing to help you find the right volume in your laptop speakers."


class REPPVolumeCalibrationMarkers(REPPVolumeCalibration):
    """
    This is a volume calibration test to be used when implementing SMS experiments with metronome sounds and REPP. It contains
    a page with general technical requirements of REPP and it then plays a metronome sound to help participants find the right volume to use REPP.

    Parameters
    ----------
    label : string
        The label for the REPPVolumeCalibration test, default: "repp_volume_calibration_music".

    materials_url: string
        The location of the REPP materials, default: https://s3.amazonaws.com/repp-materials.

    min_time_on_calibration_page : float
        Minimum time (in seconds) that the participant must spend on the calibration page, default: 5.0.

    time_estimate_for_calibration_page : float
        The time estimate for the calibration page, default: 10.0.
    """

    def __init__(
        self,
        label="repp_volume_calibration_markers",
        materials_url: str = "https://s3.amazonaws.com/repp-materials",
        min_time_on_calibration_page: float = 5.0,
        time_estimate_for_calibration_page: float = 10.0,
    ):
        super().__init__(
            label,
            materials_url,
            min_time_on_calibration_page,
            time_estimate_for_calibration_page,
        )

    def asset_calibration_audio(self, materials_url):
        return ExternalAsset(
            url=materials_url + "/only_markers.wav",
        )

    class AudioMeter(AudioMeterControl):
        decay = {"display": 0.1, "high": 0.1, "low": 0}
        threshold = {"high": -5, "low": -10}
        grace = {"high": 0.2, "low": 1.5}
        warn_on_clip = False
        msg_duration = {"high": 0.25, "low": 0.25}

    @property
    def what_are_we_playing(self):
        return "We are playing a sound similar to the ones you will hear during the experiment."


class REPPTappingCalibration(Module):
    """
    This is a tapping calibration test to be used when implementing SMS experiments with REPP.
    It is also containing the main instructions about how to tap using this technology.

    Parameters
    ----------
    label : string
        The label for the REPPTappingCalibration test, default: "repp_tapping_calibration".

    time_estimate_per_trial : float
        The time estimate in seconds per trial, default: 10.0.

    min_time_before_submitting : float
        Minimum time to wait (in seconds) while the music plays and the participant cannot submit a response, default: 5.0.

    materials_url: string
        The location of the REPP materials, default: https://s3.amazonaws.com/repp-materials.
    """

    def __init__(
        self,
        label="repp_tapping_calibration",
        time_estimate_per_trial: float = 10.0,
        min_time_before_submitting: float = 5.0,
        materials_url: str = "https://s3.amazonaws.com/repp-materials",
    ):
        super().__init__(
            label,
            join(
                PageMaker(
                    lambda assets: ModularPage(
                        label,
                        self.instructions_text(assets),
                        self.AudioMeter(
                            min_time=min_time_before_submitting, calibrate=False
                        ),
                    ),
                    time_estimate=time_estimate_per_trial,
                ),
            ),
            assets={
                "tapping_instructions_image": self.instructions_asset(materials_url),
            },
        )

    def instructions_asset(self, materials_url):
        return ExternalAsset(
            url=materials_url + "/tapping_instructions.jpg",
        )

    def instructions_text(self, assets):
        return Markup(
            f"""
            <h3>Practice how to tap on your laptop</h3>
            <hr>
            Please always tap on the surface of your laptop using your index finger (see picture)
            <ul>
                <li>Practice tapping and check that the level of your tapping is <b style="color:green;">"just right"</b>.</li>
                <li>Do not tap on the keyboard or tracking pad, and do not tap using your nails or any other bject.</li>
                <li>If your tapping is <b style="color:red;">"too quiet!"</b>, try tapping louder or on a different location on your laptop.</li>
            </ul>
            <img style="width:60%" src="{assets['tapping_instructions_image'].url}"  alt="image_rules">
            <hr>
            """
        )

    class AudioMeter(AudioMeterControl):
        decay = {"display": 0.1, "high": 0.1, "low": 0}
        threshold = {"high": -18, "low": -27}
        grace = {"high": 0.2, "low": 1.5}
        warn_on_clip = False
        msg_duration = {"high": 0.25, "low": 0.25}


class FreeTappingRecordTrial(AudioRecordTrial, StaticTrial):
    def show_trial(self, experiment, participant):
        return ModularPage(
            "free_tapping_record",
            AudioPrompt(
                self.definition["url_audio"],
                Markup(
                    """
                    <h4>Tap a steady beat</h4>
                    """
                ),
            ),
            AudioRecordControl(
                duration=self.definition["duration_rec_sec"],
                show_meter=False,
                controls=False,
                auto_advance=False,
                bot_response_media=resources.files("psynet")
                / "resources/repp/free_tapping_record.wav",
            ),
            time_estimate=self.time_estimate,
            progress_display=ProgressDisplay(
                stages=[
                    ProgressStage(
                        self.definition["duration_rec_sec"],
                        "Recording... Start tapping!",
                        "red",
                        persistent=True,
                    ),
                ],
            ),
        )

    def analyze_recording(self, audio_file: str, output_plot: str):
        from repp.analysis import REPPAnalysis
        from repp.config import sms_tapping

        plot_title = "Participant {}".format(self.participant_id)
        repp_analysis = REPPAnalysis(config=sms_tapping)
        _, _, stats = repp_analysis.do_analysis_tapping_only(
            audio_file, plot_title, output_plot
        )
        # output
        num_resp_onsets_detected = stats["num_resp_onsets_detected"]
        min_responses_ok = (
            num_resp_onsets_detected > self.definition["min_num_detected_taps"]
        )
        median_ok = stats["median_ioi"] != 9999
        failed = not (min_responses_ok and median_ok)
        stats = json.dumps(stats, cls=NumpySerializer)
        return {
            "failed": failed,
            "stats": stats,
            "num_resp_onsets_detected": num_resp_onsets_detected,
        }

    def gives_feedback(self, experiment, participant):
        return self.position == 0

    def show_feedback(self, experiment, participant):
        num_resp_onsets_detected = self.analysis["num_resp_onsets_detected"]

        if self.failed:
            return InfoPage(
                Markup(
                    f"""
                    <h4>Your tapping was bad...</h4>
                    We detected {num_resp_onsets_detected} taps in the recording. This is not sufficient for this task.
                    Please try to do one or more of the following:
                    <ol><li>Tap a steady beat, providing at least 5-10 taps.</li>
                        <li>Make sure your laptop microphone is working and you are not using headphones or earplugs.</li>
                        <li>Tap on the surface of your laptop using your index finger.</li>
                        <li>Make sure you are in a quiet environment (the experiment will not work with noisy recordings).</li>
                    </ol>
                    <b><b>If we cannot detect your tapping signal in the recording, the experiment will terminate.</b></b>
                    """
                ),
                time_estimate=5,
            )
        else:
            return InfoPage(
                Markup(
                    f"""
                    <h4>Good!</h4>
                    We could detect {num_resp_onsets_detected} taps in the recording.
                    """
                ),
                time_estimate=5,
            )


class FreeTappingRecordTest(StaticTrialMaker):
    """
    This pre-screening test is designed to quickly determine whether participants
    are able to provide valid tapping data. The task is also efficient in determining whether
    participants are following the instructions and use hardware
    and software that meets the technical requirements of REPP.
    To make the most out of it, the test should be used at the
    beginning of the experiment, after providing general instructions.
    This test is intended for unconstrained tapping experiments, where no markers are used.
    By default, we start with a warming up exercise where participants can hear their recording.
    We then perform a test with two trials and exclude participants who fail more than once.
    After the first trial, we provide feedback based on the number of detected taps. The only
    exclusion criterion to fail trials is based on the number of detected taps, by default set to
    a minimum of 3 taps. NOTE: this test should be given after a volume and a tapping calibration test.

    Parameters
    ----------

    label : string
        The label for the test, default: "free_tapping_record_test".

    performance_threshold : int
        The performance threshold, default: 0.6.

    duration_rec_sec : float
        Length of the recording, default: 8 sec.

    min_num_detected_taps : float
        Mininum number of detected taps to pass the test, default: 1.

    n_repeat_trials : float
        Number of trials to repeat in the trial maker, default: 0.

    time_estimate_per_trial : float
        The time estimate in seconds per trial, default: 10.0.

    trial_class :
        Trial class to use.
    """

    def __init__(
        self,
        label="free_tapping_record_test",
        performance_threshold: int = 0.5,
        duration_rec_sec: int = 8,
        min_num_detected_taps: int = 3,
        n_repeat_trials: int = 1,
        time_estimate_per_trial: float = 10.0,
        trial_class=FreeTappingRecordTrial,
    ):
        self.performance_check_type = "performance"
        self.performance_threshold = performance_threshold
        self.give_end_feedback_passed = False
        self.time_estimate_per_trial = time_estimate_per_trial

        nodes = self.get_nodes(duration_rec_sec, min_num_detected_taps)

        super().__init__(
            id_=label,
            trial_class=trial_class,
            nodes=nodes,
            expected_trials_per_participant=len(nodes),
            n_repeat_trials=n_repeat_trials,
            fail_trials_on_premature_exit=False,
            fail_trials_on_participant_performance_check=False,
            check_performance_at_end=True,
        )

    @property
    def introduction(self):
        return join(
            InfoPage(
                Markup(
                    """
                    <h3>Warming up</h3>
                    <hr>
                    We will now warm up with a short tapping exercise. On the next page,
                    please tap a steady beat in any tempo that you like.
                    <br><br>
                    <b><b>Attention:</b></b> Tap with your index finger and only tap on the surface of your laptop.</b></b>
                    <hr>
                    """
                ),
                time_estimate=3,
            ),
            ModularPage(
                "free_record_example",
                Markup(
                    """
                    <h4>Tap a steady beat</h4>
                    """
                ),
                AudioRecordControl(
                    duration=7.0,
                    show_meter=True,
                    controls=False,
                    auto_advance=False,
                    bot_response_media=resources.files("psynet")
                    / "resources/repp/free_tapping_record.wav",
                ),
                time_estimate=5,
                progress_display=ProgressDisplay(
                    stages=[
                        ProgressStage(7, "Recording.. Start tapping!", "red"),
                    ],
                ),
            ),
            wait_while(
                lambda participant: not participant.assets[
                    "free_record_example"
                ].deposited,
                expected_wait=5,
                log_message="Waiting for free_record_example to be deposited",
            ),
            PageMaker(
                lambda participant: ModularPage(
                    "playback",
                    AudioPrompt(
                        participant.assets["free_record_example"],
                        Markup(
                            """
                        <h3>Can you hear your recording?</h3>
                        <hr>
                        If you do not hear your recording, please make sure
                        your laptop microphone is working and you are not using any headphones or wireless devices.<br><br>
                        <b><b>To proceed, we need to be able to record your tapping.</b></b>
                        <hr>
                        """
                        ),
                    ),
                ),
                time_estimate=5,
            ),
            InfoPage(
                Markup(
                    """
                    <h3>Tapping test</h3>
                    <hr>
                    <b><b>Be careful:</b></b> This is a recording test!<br><br>
                    On the next page, we will ask you again to tap a steady beat in any tempo that you like.
                    <br><br>
                    We will test if we can record your tapping signal properly:
                    <b><b>If we cannot record it, the experiment will terminate here.</b></b>
                    <hr>
                    """
                ),
                time_estimate=3,
            ),
        )

    def get_nodes(self, duration_rec_sec: float, min_num_detected_taps: int):
        return [
            Node(
                definition={
                    "duration_rec_sec": duration_rec_sec,
                    "min_num_detected_taps": min_num_detected_taps,
                    "url_audio": "https://s3.amazonaws.com/repp-materials/silence_1s.wav",
                    # Redundant but keeping for back-compatibility
                },
                assets={
                    "stimulus": ExternalAsset(
                        url="https://s3.amazonaws.com/repp-materials/silence_1s.wav",
                    ),
                },
            )
        ]


class RecordMarkersTrial(AudioRecordTrial, StaticTrial):
    def show_trial(self, experiment, participant):
        return ModularPage(
            "markers_test_trial",
            AudioPrompt(
                self.assets["stimulus"],
                Markup(
                    """
                    <h3>Recording test</h3>
                    <hr>
                    <h3>Please remain silent while we play a sound and record it</h3>
                    """
                ),
            ),
            AudioRecordControl(
                duration=self.definition["duration_sec"],
                show_meter=False,
                controls=False,
                auto_advance=False,
                bot_response_media=resources.files("psynet")
                / "resources/repp/markers_test_record.wav",
            ),
            time_estimate=self.time_estimate,
            progress_display=ProgressDisplay(
                # show_bar=False,
                stages=[
                    ProgressStage(11.5, "Recording...", "red"),
                    ProgressStage(
                        0.5,
                        "Click next when you are ready to continue...",
                        "orange",
                        persistent=True,
                    ),
                ],
            ),
        )

    def show_feedback(self, experiment, participant):
        if self.failed:
            return InfoPage(
                Markup(
                    """
                    <h3>The recording quality of your laptop is not good</h3>
                    <hr>
                    This may have many reasons. Please try to do one or more of the following:
                    <ol><li>Increase the volumne of your laptop.</li>
                        <li>Make sure your laptop does not use strong noise cancellation or supression technologies (deactivate them now).</li>
                        <li>Make sure you are in a quiet environment (the experiment will not work with noisy recordings).</li>
                        <li>Do not use headphones, earplugs or wireless devices (unplug them now and use only the laptop speakers).</b></li>
                    </ol>
                    We will try more trials, but <b><b>if the recording quality is not sufficiently good, the experiment will terminate.</b></b>
                    <hr>
                    """
                ),
                time_estimate=5,
            )
        else:
            return InfoPage(
                Markup(
                    """
                    <h3>The recording quality of your laptop is good</h3>
                    <hr>
                    We will try some more trials.
                    To complete the experiment and get the full reward, you will need to have a good recording quality in all trials.
                    <hr>
                    """
                ),
                time_estimate=5,
            )

    def gives_feedback(self, experiment, participant):
        return self.position == 0

    def analyze_recording(self, audio_file: str, output_plot: str):
        from repp.analysis import REPPAnalysis
        from repp.config import sms_tapping

        info = {
            "markers_onsets": self.definition["markers_onsets"],
            "stim_shifted_onsets": self.definition["stim_shifted_onsets"],
            "onset_is_played": self.definition["onset_is_played"],
        }

        title_in_graph = "Participant {}".format(self.participant_id)
        analysis = REPPAnalysis(config=sms_tapping)
        output, analysis, is_failed = analysis.do_analysis(
            info, audio_file, title_in_graph, output_plot
        )
        num_markers_detected = int(analysis["num_markers_detected"])
        correct_answer = self.definition["correct_answer"]

        output = json.dumps(output, cls=NumpySerializer)
        analysis = json.dumps(analysis, cls=NumpySerializer)
        return {
            "failed": correct_answer != num_markers_detected,
            "num_detected_markers": num_markers_detected,
            "output": output,
            "analysis": analysis,
        }


class REPPMarkersTest(StaticTrialMaker):
    """
    This markers test is used to determine whether participants are using hardware
    and software that meets the technical requirements of REPP, such as
    malfunctioning speakers or microphones, or the use of strong noise-cancellation
    technologies. To make the most out of it, the markers check should be used at the
    beginning of the experiment, after providing general instructions
    with the technical requirements of the experiment. In each trial, the markers check plays
    a test stimulus with six marker sounds. The stimulus is then recorded
    with the laptop's microphone and analyzed using the REPP's signal processing pipeline.
    During the marker playback time, participants are supposed to remain silent
    (not respond).

    Parameters
    ----------

    label : string
        The label for the markers check, default: "repp_markers_test".

    performance_threshold : int
        The performance threshold, default: 1.

    materials_url: string
        The location of the REPP materials, default: https://s3.amazonaws.com/repp-materials.

    n_trials : int
        The total number of trials to display, default: 3.

    time_estimate_per_trial : float
        The time estimate in seconds per trial, default: 12.0.

    trial_class :
        The trial class to use, default: RecordMarkersTrial
    """

    def __init__(
        self,
        label="repp_markers_test",
        performance_threshold: int = 0.6,
        materials_url: str = "https://s3.amazonaws.com/repp-materials",
        n_trials: int = 3,
        time_estimate_per_trial: float = 12.0,
        trial_class=RecordMarkersTrial,
    ):
        self.n_trials = n_trials
        self.materials_url = materials_url

        self.give_end_feedback_passed = False
        self.performance_check_type = "performance"
        self.performance_threshold = performance_threshold
        self.time_estimate_per_trial = time_estimate_per_trial

        nodes = self.get_nodes()

        super().__init__(
            id_=label,
            trial_class=trial_class,
            nodes=nodes,
            expected_trials_per_participant=len(nodes),
            check_performance_at_end=True,
            assets={"rules_image": self.image_asset},
        )

    @property
    def image_asset(self):
        return ExternalAsset(
            url=f"{self.materials_url}/REPP-image_rules.png",
        )

    @property
    def introduction(self):
        return PageMaker(
            lambda assets: InfoPage(
                Markup(
                    f"""
            <h3>Recording test</h3>
            <hr>
            Now we will test the recording quality of your laptop. In {self.n_trials} trials, you will be
            asked to remain silent while we play and record a sound.
            <br><br>
            <img style="width:50%" src="{assets['rules_image'].url}"  alt="rules_image">
            <br><br>
            When ready, click <b>next</b> for the recording test and please wait in silence.
            <hr>
            """
                ),
            ),
            time_estimate=5,
        )

    def get_nodes(self):
        return [
            Node(
                definition={
                    "stim_name": f"audio{i + 1}.wav",
                    "markers_onsets": [
                        2000.0,
                        2280.0,
                        2510.0,
                        8550.022675736962,
                        8830.022675736962,
                        9060.022675736962,
                    ],
                    "stim_shifted_onsets": [4500.0, 5000.0, 5500.0],
                    "onset_is_played": [True, True, True],
                    "duration_sec": 12,
                    "correct_answer": 6,
                },
                assets={
                    "stimulus": ExternalAsset(
                        f"{self.materials_url}/audio{i + 1}.wav",
                    )
                },
            )
            for i in range(3)
        ]


class LanguageVocabularyTrial(StaticTrial):
    time_estimate = None

    def finalize_definition(self, definition, experiment, participant):
        indices = range(4)
        definition["order"] = random.sample(indices, len(indices))
        return definition

    def show_trial(self, experiment, participant):
        order = self.definition["order"]
        choices = ["correct", "wrong1", "wrong2", "wrong3"]
        image_urls = [self.assets[f"image_{choice}"].url for choice in choices]

        return ModularPage(
            "language_vocabulary_trial",
            AudioPrompt(
                self.assets["audio"],
                "Select the picture that matches the word that you heard.",
            ),
            PushButtonControl(
                choices=[choices[i] for i in order],
                labels=[
                    f'<img src="{image_urls[i]}" alt="notworking" height="65px" width="65px"/>'
                    for i in order
                ],
                style="min-width: 100px; margin: 10px; background: none; border-color: grey;",
                arrange_vertically=False,
                bot_response="correct",
            ),
        )

    def score_answer(self, answer, definition):
        if answer == "correct":
            return 1
        else:
            return 0

