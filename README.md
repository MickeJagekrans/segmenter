# HLS/DASH Server

HLS/DASH streaming server for a single file.

## Get started

Create a folder in the project root called `media` and add an .mp4 file to it.  
Start the server with `./server.py` and point your player at either one of these URLs:  

`http://localhost:8080/hls.m3u8`  
`http://localhost:8080/Manifest.mpd`  

## Transcode source file

If you want to add your own source file you will have to run the following transcoding command:  
`ffmpeg -y -i {{source file}} -c:v libx264 -r 25 -preset slow -g 50 -threads 0 -c:a aac -ar 48000 -f mp4 {{ destination file }}`

## Description

The segmenter will segment the file into 8 second chunks.  

All video and audio streams in the original file will be made available for viewing as  
separate switchable bit rate streams.  

---

### DASH

Initially I tried to split the source file into individual files and then run MP4Box  
with all streams as inputs. This did however take quite some time (~5 seconds) and was  
not optimal for direct viewing.  

I first tried to use byteranges but preparing the source file took as long as just segmenting  
it in one go.  

My solution to this was to build the .mpd manually from stream information and only  
demux + segment when the first segment request hits the server.  
The time to execute this command is about 1.5 seconds, but I would really like to get it lower than that.
