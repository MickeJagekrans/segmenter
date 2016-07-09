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
