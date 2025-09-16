# The `data` directory

The `data` directory should be used for storing media assets such as audio and video files.
Files in this directory are not included in the source code package that is deployed to the 
experiment server. To access these files in the experiment, register them as assets in your
experiment code.

For example, if you are creating nodes for a trial maker, you might write something like this:

```py
def get_nodes():
    return [
        StaticNode(
            definition={
                "stimulus_name": stimulus["name"]
            },
            assets={
                "stimulus_audio": asset(
                    stimulus["path"],
                    extension=".mp3",
                    cache=True,  # reuse the uploaded file between deployments
                )
            },
        )
        for stimulus in list_stimuli()
    ]

def list_stimuli():
    stimulus_dir = Path("data/instrument_sounds")
    return [
        {
            "name": path.stem,
            "path": path,
        }
        for path in list(stimulus_dir.glob("*.mp3"))
    ]
```

See the [PsyNet documentation](https://psynet.dev/) for more details.
