# The static directory

The static directory contains static files that are publicly accessible when the experiment
is deployed. This provides a simple way to expose files to the frontend.
A file placed in the static directory (for example, `static/{your-file-name}`) 
can be accessed at the relative URL `/static/{your-file-name}`.

The static directory also contains a symbolic link to the `assets` directory,
which is maintained by PsyNet. The `assets` directory contains static files
that are registered using PsyNet's asset management system.
See the following code example, which defines a node that is linked to an audio asset:

```python
StaticNode(
    definition={
        "stimulus_name": "audio_stimulus",
    },
    assets={
        "stimulus_audio": asset("data/audio_stimulus.mp3)
    },
)
```

You can get away with the simple approach (just placing files in the `static` directory)
if you are just using a small number of static files, but for substantial collections
(e.g. experimental stimuli) it is recommended to use PsyNet's asset management system.
