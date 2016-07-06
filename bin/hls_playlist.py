import os, json
from subprocess import check_output
from operator import itemgetter

#AUDIO_ENTRY_FORMAT = '#EXT-X-MEDIA:GROUP-ID="audio{0}",LANGUAGE="{1}",TYPE=AUDIO,AUTOSELECT=YES,DEFAULT=NO,URI="audio/{2}.m3u8"'
AUDIO_ENTRY_FORMAT = '#EXT-X-MEDIA:GROUP-ID="audio{0}",LANGUAGE="{1}",TYPE=AUDIO,AUTOSELECT=YES,DEFAULT=NO,URI="audio/{2}.m3u8"'
VIDEO_ENTRY_FORMAT = '#EXT-X-STREAM-INF:PROGRAM-ID=1,AUDIO="audio{0}",RESOLUTION={1},BANDWIDTH={2}'
SEGMENT_LENGTH = 8

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def build_master(source_path):
    master = ['#EXTM3U', '#EXT-X-VERSION:4', '#EXT-X-PLAYLIST-TYPE:VOD']

    streams = get_streams(source_path)

    for i, s in enumerate(streams[0]):
        entry = AUDIO_ENTRY_FORMAT.format(i, s['tags']['language'], s['bit_rate'])
        master.append(entry)

    # TODO: add CODECS
    for i, s in enumerate(streams[1]):
        bit_rate = s['bit_rate']
        resolution = '{0}x{1}'.format(s['width'], s['height'])
        bandwidth = int(bit_rate) + int(streams[0][i]['bit_rate'])
        entry = VIDEO_ENTRY_FORMAT.format(i, resolution, bandwidth)
        master.append(entry)
        master.append('video/{0}.m3u8'.format(bit_rate))

    return '\n'.join(master)

def build_playlist(source_path, playlist_type, bit_rate):
    mkdir('static/{0}/{1}'.format(playlist_type, bit_rate))

    target_duration_tag = '#EXT-X-TARGETDURATION:{0}'.format(SEGMENT_LENGTH)
    playlist = ['#EXTM3U', '#EXT-X-VERSION:4', target_duration_tag, '#EXT-X-PLAYLIST-TYPE:VOD', '#EXT-X-MEDIA-SEQUENCE:1']

    duration = get_duration(source_path)
    segment_count = int(duration // 8)

    for i in range(segment_count):
        playlist.extend([
            '#EXTINF:{0}.0'.format(SEGMENT_LENGTH),
            os.path.join(str(bit_rate), '{0}.ts'.format(i))
            #os.path.join(playlist_type, str(bit_rate), '{0}.ts'.format(i))
        ])

    playlist.extend([
        '#EXTINF:{0}'.format(duration % SEGMENT_LENGTH),
        os.path.join(str(bit_rate), '{0}.ts'.format(segment_count)),
        #os.path.join(playlist_type, str(bit_rate), '{0}.ts'.format(segment_count)),
        '#EXT-X-ENDLIST',
        ''
    ])

    return '\n'.join(playlist)

# TODO: extract to separate file
def get_streams(source_path):
    # TODO: return only important properties
    cmd = 'ffprobe -print_format json -show_streams -v error {0}'.format(source_path)
    streams = json.loads(check_output(cmd.split()).decode('utf-8'))['streams']

    audio = sorted([s for s in streams if s['codec_type'] == 'audio'], key=lambda k: int(k['bit_rate']))
    video = sorted([s for s in streams if s['codec_type'] == 'video'], key=lambda k: int(k['bit_rate']))

    return [audio, video]

def get_duration(source_path):
    cmd = 'ffprobe -print_format json -v error -show_format {0}'.format(source_path)
    output = json.loads(check_output(cmd.split()).decode('utf-8'))
    return float(output['format']['duration'])
