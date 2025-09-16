# pylint: disable=missing-class-docstring,missing-function-docstring

import psynet.experiment
from psynet.modular_page import (
    AudioPrompt,
    ImagePrompt,
    ModularPage,
    PushButtonControl,
    TextControl,
    AudioRecordControl,
)
from psynet.page import InfoPage
from psynet.timeline import Event, ProgressDisplay, ProgressStage, Timeline


def get_timeline():
    return Timeline(
        InfoPage(
            """
            The InfoPage displays text to the participant without collecting any response.
            """,
            time_estimate=5,
        ),
        ModularPage(
            label="push_button_page",
            prompt="""
            More complex pages are typically implemented as ModularPages,
            which allow you to combine arbitrary 'Prompts' with arbitrary 'Controls'.
            This example combines the default text prompt with a push-button control.

            I hope that was clear?
            """,
            control=PushButtonControl(
                choices=["Yes, it was clear", "Sorry, it was not clear"],
            ),
            time_estimate=5,
        ),
        ModularPage(
            label="image_prompt",
            prompt=ImagePrompt(
                "static/images/lake_mirror_reflection_yosemite.jpg",
                text="""
                This is an example of an image prompt.
                Here we've placed the image in the static directory.
                """,
                width="767px",
                height="512px",
                margin_bottom="25px",
            ),
            time_estimate=5,
        ),
        ModularPage(
            label="audio_prompt",
            prompt=AudioPrompt(
                "static/audio/clarinet.mp3",
                text="""
                This is an example of an audio prompt, again using the static directory.
                We've combined it with a text control, which allows the participant to type in free text.
                """,
            ),
            control=TextControl(),
            time_estimate=5,
        ),
        ModularPage(
            label="audio_prompt_and_record",
            prompt=AudioPrompt(
                "static/audio/clarinet.mp3",
                text="""
                Here's a more complex example, where we play some audio and then record from the
                participant's microphone.
                """,
                play_window=[0, 3.0]
            ),
            control=AudioRecordControl(
                duration=3.0,
                bot_response_media="static/audio/clarinet.mp3",
            ),
            time_estimate=10.0,
            events={
                "recordStart": Event(is_triggered_by="promptEnd", delay=0.5),
            },
            progress_display=ProgressDisplay(
                stages=[
                    ProgressStage([0.0, 3.0], "Listen...", "blue"),
                    ProgressStage([3.0, 3.5], "Get ready...", "orange"),
                    ProgressStage([3.5, 6.5], "Recording...", "red"),
                    ProgressStage(
                        [6.5, 7.0], "Finished recording.", "blue", persistent=True
                    ),
                ],
            )
        )
    )


class Exp(psynet.experiment.Experiment):
    timeline = get_timeline()
