from psynet.bot import Bot
from psynet.modular_page import TimedPushButtonControl
from datetime import datetime


class SingleTimedPushButtonControl(TimedPushButtonControl):
    def __init__(self, label, button_highlight_duration=0.75):
        assert isinstance(label, str)
        super().__init__(
            choices=[label],
            arrange_vertically=True,
            button_highlight_duration=button_highlight_duration
        )

    def format_answer(self, raw_answer, **kwargs):
        event_log = kwargs["metadata"]["event_log"]
        participant = kwargs["participant"]

        if isinstance(participant, Bot):
            event_log.append({
            "eventType": "promptStart",
            "localTime": "2025-07-29T14:50:04.304Z",
            "info": None,
        })

        audio_start = [t['localTime'] for t in event_log if t['eventType'] == 'promptStart']
        push_button_times = [t['localTime'] for t in event_log if t['eventType'] == 'pushButtonClicked']

        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

        audio_start_time = datetime.strptime(audio_start[0], date_format)
        push_button_times = [datetime.strptime(t, date_format) for t in push_button_times]

        return [(p - audio_start_time).total_seconds() for p in push_button_times]
