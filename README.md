# Webcam Data Extraction — Texas and Jackson Hole

During my time at Baylor University, I worked on collecting images from publicly available webcam feeds in Texas and Jackson Hole, Wyoming. My goal was to turn live camera sources into organized imagery that could be processed and analyzed rather than only viewed in real time.

I developed two workflows: one to discover and download images from Texas Department of Transportation (TxDOT) roadway cameras, and another to capture still frames from Jackson Hole live video streams. I've kept my original scripts in [original/](original/) and reorganized the newer versions in [scripts/](scripts/) so they can run without my old computer's directory structure.

## Texas roadway cameras

I used Selenium to visit TxDOT district camera pages, scroll through their listings, and extract camera names and image addresses. I then downloaded available snapshots and recorded cameras that could not be retrieved. My original workflow covered all 24 TxDOT district codes.

The updated [TxDOT script](scripts/txdot_frames.py) combines discovery and optional downloads. It creates a CSV manifest with camera names, source URLs, download status, and saved file paths.

```bash
python scripts/txdot_frames.py --districts DAL HOU --download --output-dir outputs/txdot
```

This script collects still images on each run; it does **not** automatically schedule captures every 15 minutes or generate a continuous video. Scheduling repeated runs is a separate step. The current TxDOT page structure may also differ from the original.

## Jackson Hole live streams

For Jackson Hole, I used Streamlink and M3U8 playlists to access live video segments, then OpenCV to extract frames. My original script read camera names and URLs from an Excel sheet and recorded failed feeds.

The updated [Jackson Hole script](scripts/jackson_hole_frames.py) accepts a CSV or Excel feed list, uses Streamlink to discover a playable stream, and uses FFmpeg to save JPEG frames at a configurable interval. It records successes and failures.

```bash
python scripts/jackson_hole_frames.py --feeds samples/feeds.example.csv --frames 3 --interval 15 --output-dir outputs/jackson_hole
```

The example feed list is only a template. Replace it with URLs you are authorized to access.

## Setup

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m unittest discover -s tests
```

The Texas workflow requires Chrome and Selenium. The Jackson Hole workflow also requires **FFmpeg** on the system PATH.

## Files

- [TxDOT camera extraction](scripts/txdot_frames.py)
- [Jackson Hole stream extraction](scripts/jackson_hole_frames.py)
- [Original Baylor scripts](original/)
- [Example feed list](samples/feeds.example.csv)
- [Offline parser tests](tests/)

## Reproducibility and limitations

I've removed my hard-coded Windows paths and made the input and output locations configurable. However, these workflows depend on third-party sites and streams, and I haven't verified end-to-end capture against the current services. I haven't included archived footage or images because availability and redistribution permissions may vary.

Use only sources where automated collection and recording are permitted, and respect provider terms and reasonable request rates.

The historical scripts also remain in my [Baylor Portfolio-Code-Examples repository](https://github.com/jayjayanton/Portfolio-Code-Examples/tree/main/Baylor%20Projects/Webscraping).
