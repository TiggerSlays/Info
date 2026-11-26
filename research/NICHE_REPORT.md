# Niche research: is "Brain Glitch" the right niche?

*Researched 26 Nov 2026. Data comes from public vidIQ channel pages (`vidiq_scan.py`,
raw output in `scan1.json` and `scan2.json`) and AIR Media-Tech's 2026 study of
Shorts revenue across 274 channels, which uses real YouTube Studio data.*

## Short answer

**The optical-illusion idea is unproven. As a Shorts-only channel it won't make
much money. It is worth keeping only in a changed form:** interactive perception
tests in Shorts for reach, plus longer explainer videos in the Education category
for revenue. Running it as a 30-day test with a clear stop rule is better than
committing blind.

## What I measured

The tutorial's checklist asks for real channels in the niche, their views over the
last 28 days, how often they upload, whether recent uploads still perform, and how
crowded the niche is. I scanned 30 channels across five niches that this pipeline
could produce.

| Niche | Leading channels found (views per day, last 28 days) | What the data says |
|---|---|---|
| **Optical illusions** | **None.** Every "illusion" channel I found was tiny (1.6k subscribers, 0 views a day) or mislabelled ("Illusion Entertainment" is Bangladeshi comedy drama). Puzzle guy's one illusion Short got 33k views. | Either nobody has cracked it or demand is weak. **The data can't tell which.** |
| **Interactive tests and quizzes** | Vin 1.55M a day (30 uploads in 28 days, recent Shorts 150–340k each). MacaQuiz 388k a day. Great Quiz 245k a day (kids). | **Strong demand**, but **crowded, with many dying channels**: Curious Shorts (2.3M subscribers, 0 uploads), QUIZZER KAYRA (403 views a day), Guessr, and Puzzle guy (peaked at 95M-view Shorts in 2022, now 20k a day). This is the tutorial's warning sign: "a pool of bad performers". |
| **Faceless science and curiosity facts** | Zack D. Films 88.7M a day (136 uploads in 28 days). The Infographics Show 2.05M a day. Bright Side 554k a day. | **Huge demand.** Zack D. Films proves the "curious fact" Short at enormous scale. The top is dominated by very large studios. |
| **Marble and physics simulations** | Jelle's Marble Runs 99k a day (mostly long-form). ONE Marble RUN 375k a day, almost all from one 98M-view Short. Marble Race King 18k a day. | Real demand, but driven by single viral hits, and the biggest channels film real marbles. Simulation-only channels I found were small. |
| **Data comparisons** | Pure Data Comparison 137k a day (long-form only, Shorts are dead). Compared Comparison 27k a day (3 uploads). Random Comparison 85 a day. | **Weakest.** The Shorts format has faded, and the money is in long-form. |

## The money

- **Shorts pay 3–14% of what long-form pays per view.** For most channels, Shorts
  are **under 2% of total revenue**. Typical Shorts RPM outside music is
  **$0.02–$0.20 per 1,000 views** (AIR Media-Tech, 274 channels, full-year medians).
- **Education and Science has the highest long-form RPM in that study: $15–18 per
  1,000 views.** Entertainment long-form is roughly $2–5.
- vidIQ's estimates, all made the same way, point the same direction:
  - **Zack D. Films**: about 2.5B Shorts views in 28 days → estimated **$84k**.
  - **The Infographics Show**: about 57M long-form views in 28 days → estimated **$210k**.
- **Starting 1 February 2027**, Shorts ad revenue requires **10M qualified Shorts views
  in 90 days**. A Shorts-only channel earns nothing until it clears that. Long-form can
  monetize through 4,000 watch hours plus 1,000 subscribers, and Shorts views don't
  count toward those watch hours.
- The tutorial's own screenshot (60.5M views → $10.5k, about $0.17 per 1,000) sits
  at the top of the normal Shorts range.

**Bottom line:** at a realistic $0.05–0.15 per 1,000 views, **10M Shorts views a month
is about $500–1,500.** Getting to real income from Shorts alone takes tens of
millions of views every month.

## How I'd rank the options for this pipeline

| Rank | Option | Demand | Competition | Pay | Can the pipeline make it? | Verdict |
|---|---|---|---|---|---|---|
| 1 | **Perception tests + "why your brain does this"** (Shorts) **with weekly long-form explainers** (Education) | Proven for tests (Vin) and curiosity science (Zack D.). **Unproven for illusions specifically** | Medium: no dedicated illusion leader | Shorts low, long-form **high** | **Yes, already built** | **Best fit. Test it.** |
| 2 | Animated "curious facts" (Zack D. style) | Highest | **Very high**, dominated by giant studios | Shorts low | Partly: needs stronger visuals | Big upside, hard to break in |
| 3 | Physics / marble simulations | Driven by viral hits | Medium | Low (Lifestyle and kids audience) | Yes, with a physics engine | Lottery-ticket profile |
| 4 | Generic quizzes / emoji tests | Real | **Crowded and decaying** | Low, and kids-heavy, which cuts ad revenue | Yes | Avoid as a main niche |
| 5 | Data comparisons | Fading on Shorts | Low | Long-form only | Yes | Avoid for Shorts |

## Recommended changes to Brain Glitch

1. **Make Shorts interactive, not explainers.** Vin's consistent hooks are tests aimed
   at the viewer: "Only 3% can see it", "Your brain is lying to you, test it", "Are
   you a ___? test". The viewer takes part, which drives replays. Illusions become the
   test, and the explanation is the payoff.
2. **Add one long-form video a week** (8–12 min, Education category). For example:
   "20 illusions that prove your brain is lying to you, and the science of each." The
   same scenes and voice pipeline work. This is where the $15–18 RPM is. The AIR study
   also found channels posting **one Short for every 2–3 long-form videos** did best on
   both revenue and subscribers.
3. **Widen the content pool beyond about 60 classic illusions:** colour and memory
   tests, attention tests ("count the passes"), audio illusions, cognitive biases and
   reaction-time tests. This also protects against YouTube's
   [inauthentic content policy](https://support.google.com/youtube/answer/1311392),
   which demonetizes repetitive, templated output.
4. **Aim for adults in the US, UK and Canada.** Avoid anything kid-coded: cartoons,
   "kids quiz" wording, bright toy colours. Kids-heavy audiences cut ad revenue sharply.

## 30-day test and stop rule

- Post **1 Short a day + 1 long-form a week** for 30 days on a warmed-up channel.
- **Keep going** if any Short passes **50k views**, or the median of the last 10 Shorts
  exceeds **2k**, with about 80% of viewers not swiping away.
- **Pivot** if after 30 Shorts the median is under 1k with no breakout. Option 2
  (curious facts) is the next one to test with the same pipeline.

## Limits of this research

- I found channels through web search and vidIQ, not YouTube's own search (direct
  API access was blocked), so I may have missed illusion channels. The sample is
  about 30 channels.
- vidIQ revenue figures are modelled estimates with an unstated time window. Use them
  to compare channels, not as real income.
- "Views per day" is the channel total, including long-form. I checked each channel's
  latest videos table to see which format the views come from.
- Only real analytics from your own channel (swipe rate, average view percentage, RPM)
  can settle this. That's what the 30-day test is for.

## Sources
- [vidIQ channel stats pages](https://vidiq.com/youtube-stats/), e.g. [Vin](https://vidiq.com/youtube-stats/channel/@vinrl/), [Zack D. Films](https://vidiq.com/youtube-stats/channel/@zackdfilms/), [The Infographics Show](https://vidiq.com/youtube-stats/channel/@TheInfographicsShow/), [Puzzle guy](https://vidiq.com/youtube-stats/channel/@puzzleguy/), [ONE Marble RUN](https://vidiq.com/youtube-stats/channel/UC6lzuoJrM2w94vZw6cWuGqg/), [Pure Data Comparison](https://vidiq.com/youtube-stats/channel/UC6x7Z0GtWqvSs7k-ItP1ZJQ)
- [AIR Media-Tech: YouTube Shorts RPM niche by niche, 274 channels (2026)](https://air.io/en/air-data-findings/what-is-youtube-shorts-rpm-in-your-niche-in-2026)
- [Viibeo: YouTube inauthentic content policy 2026](https://www.viibeo.com/blog/faceless-youtube-inauthentic-content-policy-2026), [Metricool: Shorts algorithm 2026](https://metricool.com/youtube-shorts-algorithm/)
