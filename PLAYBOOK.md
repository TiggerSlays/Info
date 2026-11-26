# The faceless Shorts playbook

This is a breakdown of a 54-minute tutorial posted on X by @noblehq__ (25 Nov 2026),
"how to monetize a YouTube channel with AI without showing your face". I downloaded
the whole video, transcribed it with Whisper and went through it frame by frame. Each
step below says what the tutorial teaches and how this repo applies it.

> **Context.** The tutorial is a sales funnel for a paid Shorts mentorship
> ("Earnit Media"). The last 4 minutes are the pitch. The earnings it shows
> (about $10.5k a month and $103k over 90 days) are screenshots I can't verify.
> The method below is still sound. Its source of footage is the exception (see step 3).

---

## Step 1: Find a "banger niche" (00:00 to 09:50)

**What the tutorial teaches**
- Scroll YouTube Shorts while logged out. Open a tab for every promising channel.
  Spend 1 to 2 hours on this and compare several channels before choosing.
- A good niche has **lots of views, a high ceiling (it can go viral), steady
  performance and few competitors**.
- An **English voiceover** is a plus. It draws a US audience, which pays a higher
  RPM, and it makes monetization more likely.
- Pick formats that take **little effort**, so you can out-produce the current channels.
- Look for **outliers**, meaning videos that got far more views than the rest of a
  channel's uploads. Only count **recent** ones (the last few weeks, not a year ago).
  Then build a sub-niche around the outliers alone.
- Compare a channel's outliers with its flops to find the pattern that matters.
  In the tutorial's example, the outliers were "how do they do this?" videos and the
  flops were "why" stories.
- vidIQ (a free extension) shows a channel's views over the last 30 days. Look for
  **more than 50M views in 30 days with regular uploads**.
- **Saturation check.** Paste an outlier's title into YouTube search and filter to
  Shorts. A few channels doing well in the niche is a green light. Many channels
  making the same content, with some of them flopping, is a red flag.

**What this repo does:** it uses the **optical illusions / "brain glitch"**
niche. It has the same pull as the tutorial's outliers ("how is this possible?
the method will shock you"), needs no face, and every visual can be drawn in code.

## Step 2: Set up the channel and branding (09:50 to 13:50)

**What the tutorial teaches**
- Create a Gmail account and channel. **Warm it up for a couple of days** by watching
  videos like a normal user. An older account with real watch history is better
  because YouTube trusts it more.
- Spend **no more than 10 minutes on branding**. Have an AI make the profile picture,
  then the 2560×1440 banner. AI tools often ignore the size, so be specific.
- Ask an AI for 20 short, memorable channel names, then set the @handle to match.

**What this repo does:** `shorts_factory/channel_kit.py` → `output/channel/`
builds an 800×800 avatar and a 2560×1440 banner with text inside the safe area.
Both use the café-wall pattern, so the brand matches the content.

## Step 3: Make the video (13:50 to 44:50). This is the core

### 3a. Ideas
- Work out *why* the competitor's outliers go viral (here, curiosity about how a
  trick works). Then use AI to brainstorm new ideas with the same pull. Give it
  full context, because "AI is only as good as you prompt it".
- **"Copy with style."** Keep the structure and add your own angle. Copying a
  video exactly won't win the niche.
- Check how many clips, what pacing and which overlays the outlier uses.

### 3b. Script
- A structure for retention, shown on screen at 20:00:
  **Hook (0–3s) → problem / curiosity build (3–10s) → payoff / twist (10–45s).**
- The tutorial takes the competitor's script from a transcript site and swaps in
  its own topic ("This couple tried the ___ trend where ___. And while most people
  thought they completed the trend, the last guy showed exactly how to do it, and
  the method will shock you.").

### 3c. AI voiceover (ElevenLabs)
- Use an **American, young, male, conversational voice** from the Voice Library,
  filtered to English → American → Social media.
- **Generate one sentence at a time**, not the whole script. One bad take then
  doesn't force a full redo, and it saves credits.
- Say each line aloud first, then regenerate until the voice matches.
- If the voice glitches, adjust stability, similarity and style exaggeration.

### 3d. Edit (DaVinci Resolve; CapCut works too)
- Cut every gap in the voiceover so the pace stays tight. Use ripple-delete shortcuts.
- **The hook must grab attention on mute**, so put the most visually engaging clip
  first. More movement is better.
- The tutorial targets **about 16 to 20 seconds**, matching the competitor.
- **Music:** use the same track on every video, low under the voice, with the
  **beat drop on the payoff**. Raise the volume with keyframes.
- **Zoom:** put an adjustment layer over every clip with a slow push-in, and zoom
  faster on key moments.
- **Overlays:** a red circle that pops in (small, then quickly larger) and tracks
  the subject, and a red arrow with a pop-in. Add a subtle camera shake.
- **Colour grade:** a little more saturation and contrast, plus sharpening.
- **SFX:** a click, shutter or pop on each overlay, kept quiet so it never jars.
- **Captions:** split them the way the line is spoken. Never let one run across
  a cut. Use a bold font with stroke and drop shadow, and highlight key words.
- Export at 60 fps with a high bitrate.
- Title in the competitor's style ("___ Trend Goes VIRAL!").

**What this repo does** (`shorts_factory/make_short.py`):

| Tutorial | This repo |
|---|---|
| Hook / curiosity / payoff script | Each script JSON is written in that structure |
| ElevenLabs, generated line by line | Kokoro neural TTS, **one segment at a time**, silences trimmed |
| Cut voiceover gaps | Silences trimmed automatically, with a fixed 0.14s breath between lines |
| Visual hook first | The illusion is on screen from frame 1 |
| Slow zoom on an adjustment layer | Push-in on every segment, alternating punch-in on cuts |
| Red circle / arrow with pop-in | `callouts` pop in on a **specific spoken word** (`at_word`) |
| Quiet SFX on overlays and cuts | Whoosh on cuts, pop on callouts |
| Music low under the voice | Generated lo-fi bed at −22 dB |
| Captions split by phrasing, never across cuts | Whisper word timings, at most 3 words, never overlapping, spoken word in yellow |
| Bold font, stroke, shadow | Inter Black with a 7px outline and a shadow |
| Export settings | H.264 at CRF 19, AAC 192k, loudness normalized to about −14 LUFS |

### What I dropped, and why
| Tutorial step | Problem | Replacement here |
|---|---|---|
| Download other creators' TikToks (SaveTT) and re-upload them | Copyright infringement. YouTube's **reused content** policy also blocks monetization for this. Channels get demonetized or struck. | Every frame is generated in code and owned by the channel |
| Shazam the competitor's (commercial, sped-up) song and rip it | Content ID claims the revenue or blocks the video | Music generated in code |
| Copy the competitor's transcript | Fine as a template. Copied word for word, it's plagiarism | Original scripts that follow the same *structure* |

## Step 4: Posting, stats and "view jail" (44:50 to 50:10)

- **Post daily** and set aside **2 hours a day**. Consistency is what drives results.
- **"0-view jail" protocol:** if an upload gets 0 views, wait a day and post again.
  If that gets 0 too, wait 2 days. If it still gets 0, start a fresh (warmed-up)
  channel. (This is fine for a new channel with no reach. Never use a new channel
  to dodge strikes. YouTube treats that as circumvention.)
- **The "10–30k jail"** isn't a real jail. Keep posting. Breakouts usually start
  **above about 40k views**.
- **Double down** on whichever format, sub-genre or topic beats the rest. Keep
  using it until it stops getting views, then move to the next one.
- **Targets:** a **viewed-vs-swiped rate of about 80%**, and **average percentage
  viewed (APV) above 100%**. A 15-second Short should aim for about 130%, because
  replays count. If either is low, change the pacing, topic or hook.
- **Monetization:** Shorts need **10M valid views in 90 days**. The YouTube Partner
  Program also needs **1,000 subscribers**. Then link AdSense.

## Step 5: Scale and outsource (50:10 to 54:30)

- **Don't outsource too soon.** Make viral videos yourself first, or you won't
  know what to tell an editor.
- Hire only once the main channel makes **about $1,000 a month** and you can go
  viral consistently. Hand off the work you like least (usually editing).
- Train people well: step-by-step SOPs, daily contact, and make yourself easy to
  work for.
- **Only then start more channels.** Avoid "shiny object syndrome". The aim is a
  stack of channels that keep running without you.
- In this repo, **the SOP is the code.** A new episode is one new script JSON.
  An editor, or an AI, writes the script and the pipeline does the rest.

---

## Daily routine for this channel

1. **Research (15 min).** Check the competitor channels' recent outliers and note any
   new illusions or hook styles that are working.
2. **Write (15 min).** Copy `shorts_factory/scripts/illusions_01.json`, write the
   hook, curiosity and payoff lines, and choose scenes and callouts.
3. **Render (5 min).** Run `python make_short.py scripts/<new>.json`, then watch it
   once with sound and once on mute.
4. **Upload.** Use `output/<slug>_upload.json` for the title, description and tags.
5. **Review (weekly).** Check swipe rate and APV in YouTube Studio, then keep or
   change the hook style, length and scenes.
