# Brain Glitch: a faceless YouTube Shorts studio

This repo applies the method from a 54-minute tutorial on running a faceless,
monetised YouTube Shorts channel (posted on X by @noblehq__). It has two parts:

| | |
|---|---|
| [`PLAYBOOK.md`](PLAYBOOK.md) | What the tutorial teaches, step by step, with what I kept, changed and dropped. |
| [`shorts_factory/`](shorts_factory) | A pipeline that turns a script file into a finished Short. |
| [`output/`](output) | The finished Shorts, thumbnails, upload text and channel branding. |

## Why the method was changed

The tutorial's channel downloads other creators' TikTok trend clips and
re-uploads them with an AI voiceover. That breaks copyright. It also falls under
YouTube's "reused content" policy, which can demonetise or remove a channel.
This studio keeps the skills from the tutorial (picking a niche, the script
structure, the voiceover, the caption style, the edit, the posting schedule)
and generates every frame and sound from scratch. The channel owns all of it.

## Pipeline

```
script.json ──► Kokoro TTS voiceover ──► Whisper word timings ──► word-by-word captions (ASS)
           └──► code-rendered scenes + punch-in zooms + red circle/arrow callouts
                └──► whoosh/pop SFX + generated lo-fi music bed at -22 dB
                     └──► ffmpeg ──► 1080x1920 MP4 + thumbnail + upload JSON
```

```bash
cd shorts_factory
./setup.sh                                   # deps + open-source voice model (no API keys)
python make_short.py scripts/illusions_01.json
python channel_kit.py --name "BRAIN GLITCH"  # 800x800 avatar + 2560x1440 banner
```

To make a new Short, copy a script in `shorts_factory/scripts/`. Then change the text,
the scene for each segment, and the callouts. A callout can fire on a spoken word
(`"at_word": "tilted,"`). New visuals go in `shorts_factory/scenes.py` as one
function each.

Everything runs locally. The voice is Kokoro-82M (Apache-2.0), the captions use
OpenAI Whisper (MIT), and the music and SFX are generated in code.
