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

### Example: extracting TxDOT camera snapshots

For example, I can collect the camera images currently available for the Dallas (`DAL`) and Houston (`HOU`) districts:

```bash
python scripts/txdot_frames.py --districts DAL HOU --download --output-dir outputs/txdot
```

The script opens each district's camera page with Selenium, scrolls to load camera cards, and uses BeautifulSoup to find the camera names and image URLs. With `--download`, it requests each image and saves the returned image bytes to a district folder. It also writes `camera_manifest.csv` with the camera name, URL, saved path, and download status.

A successful run would produce a structure like this (camera names are illustrative):

```text
outputs/txdot/
├── DAL/
│   ├── 0001_Example_Dallas_Camera.jpg
│   └── 0002_Another_Dallas_Camera.jpg
├── HOU/
│   └── 0001_Example_Houston_Camera.jpg
└── camera_manifest.csv
```

Each JPEG is a **still snapshot returned by a camera image URL**, not a frame decoded from a video recording. Running the script again in the same directory can overwrite snapshots with the same filenames. To build a historical series, I would schedule repeated runs into separate timestamped output directories, for example `outputs/txdot/2026-11-02_1500/` and `outputs/txdot/2026-11-02_1515/`. The script does not currently schedule those runs or create timestamped directories automatically.

## Jackson Hole live streams

For Jackson Hole, I used Streamlink and M3U8 playlists to access live video segments, then OpenCV to extract frames. My original script read camera names and URLs from an Excel sheet and recorded failed feeds.

The updated [Jackson Hole script](scripts/jackson_hole_frames.py) accepts a CSV or Excel feed list, uses Streamlink to discover a playable stream, and uses FFmpeg to save JPEG frames at a configurable interval. It records successes and failures.

```bash
python scripts/jackson_hole_frames.py --feeds samples/feeds.example.csv --frames 3 --interval 15 --output-dir outputs/jackson_hole
```

The example feed list is only a template. Replace it with URLs you are authorized to access.

### Example: extracting Jackson Hole video frames

For Jackson Hole, I first supply a CSV containing the camera names and the live-stream page URLs. For example, the input structure is:

```csv
Name,Link
Example_Jackson_Hole_Camera,https://example.org/authorized-live-stream
```

That URL is only a placeholder; it must be replaced with a real, permitted stream URL. I can then run:

```bash
python scripts/jackson_hole_frames.py --feeds data/jackson_hole_feeds.csv --frames 3 --interval 15 --output-dir outputs/jackson_hole
```

The updated script uses Streamlink to resolve the video feed, then FFmpeg to decode the stream and save three JPEG frames at a nominal 15-second sampling interval. Here, `--interval 15` means **15 seconds between extracted frames**, not a 15-minute recurring collection schedule.

A successful run would create files like:

```text
outputs/jackson_hole/
├── Example_Jackson_Hole_Camera/
│   ├── Example_Jackson_Hole_Camera_001.jpg
│   ├── Example_Jackson_Hole_Camera_002.jpg
│   └── Example_Jackson_Hole_Camera_003.jpg
└── capture_log.csv
```

Unlike the TxDOT snapshots, these images are **decoded frames from a live video stream**. In my original Baylor script, I downloaded short video segments and used OpenCV to save up to three consecutive frames into a `Photos/` folder. The updated script uses FFmpeg instead, and saves images into a separate directory for each camera. It does not retain the source MP4 segments.

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
