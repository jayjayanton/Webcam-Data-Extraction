
# pip install urllib
# pip install m3u8
# pip install streamlink
import urllib
import m3u8
import streamlink
import os
import glob
import cv2
import datetime
import pandas as pd

parent_dir = "G:/Webscrapping/"
now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S' )

video_dir = f"G:/Webscrapping/Webcam_{now}"
# Path
path = os.path.join(parent_dir, video_dir)
os.mkdir(path)

photo_dir = f"Photos"
# Path
photo_path = os.path.join(path, photo_dir)
os.mkdir(photo_path)

def get_stream(url):
    """
    Get upload chunk url
    """
    streams = streamlink.streams(url)
    stream_url = streams["best"]

    m3u8_obj = m3u8.load(stream_url.args['url'])
    return m3u8_obj.segments[0]
    

def dl_stream(url, filename, chunks):
    """
    Download each chunks
    """
    pre_time_stamp = -120
    for i in range(chunks+1):
        stream_segment = get_stream(url)
        cur_time_stamp = \
            stream_segment.program_date_time.strftime(now)

        if pre_time_stamp == cur_time_stamp:
            pass
        else:
            # print(cur_time_stamp)
            file = open(f"{filename}_{str(cur_time_stamp)}.mp4", 'ab+')
            with urllib.request.urlopen(stream_segment.uri) as response:
                html = response.read()
                file.write(html)
            pre_time_stamp = cur_time_stamp


file = pd.read_excel("youtube feeds.xlsx")

Missing_Webcams = f"{now}.txt"
with open(os.path.join(path, Missing_Webcams), 'a') as fp:
    pass

    for index, row in file.iterrows():
        try:
            Name = (row['Name'])
            Url = (row['Link'])

            outputdir = os.path.join(video_dir,Name)
            dl_stream(Url, outputdir ,1)
        except:
            # print(f"{Name}:{Url}")
            fp.write(f"{Name}:{Url}\n")
            continue
fp.close()

os.chdir(video_dir)
Videos = sorted(glob.glob("*.mp4"))

for file in Videos:
    vidcap = cv2.VideoCapture(file)
    success,image = vidcap.read()
    count = 0

    baseConfilename = os.path.basename(file)
    # print(baseConfilename)

    CleanBaseStr = os.path.splitext(baseConfilename)[0]
    Reclass_Split = CleanBaseStr.split("_")[0]
    while success:
      cv2.imwrite(os.path.join(photo_dir,f"{CleanBaseStr}_%d.jpg" %count), image)
      count += 1
             # save frame as JPEG file
      success,image = vidcap.read()
      if count >=3:
          break

print("done processing \n")
