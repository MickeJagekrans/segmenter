# HLS/DASH Server

HLS/DASH streaming server for a single file.

## Get started

Create a folder in the project root called `media` and add an .mp4 file to it.  
Start the server with `./server.py` and point your player at either one of these URLs:  

`http://localhost:8080/hls.m3u8`  
`http://localhost:8080/Manifest.mpd`  

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

My solution to this was to build the .mpd manually from stream information and split the streams  
in a background process, returning the .mpd as soon as possible.  
When the split command is done (almost instantaneous) I fire off the segmentation commands  
in background processes and wait for the files to exist on the first segment request.  
This ensures a quick response time.
