import os, json
from subprocess import Popen, check_output, call

STREAM_PATH_TMPL = ' tmp/{0}'

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def sort(streams, codec_type):
    return sorted([s for s in streams if s['codec_type'] == codec_type], key=lambda k: int(k['bit_rate']))

def get_streams(input_file):
    cmd = 'ffprobe -v quiet -show_streams -print_format json {0}'.format(input_file)
    streams = json.loads(check_output(cmd.split()).decode('utf-8'))['streams']
    return [sort(streams, 'audio'), sort(streams, 'video')]

def get_cmd_part(idx, codec_type):
    ext = 'mp4' if codec_type == 'video' else 'm4a'
    return ' -map 0:{0} -c copy tmp/{0}.{1}'.format(idx, ext)

def segment():
    path = os.path.join('static', 'dash')
    mkdir(path)
    cmd = 'MP4Box -dash 8000 -frag 8000 -rap -segment-name seg_%s -url-template -out {0}/Manifest.mpd'.format(path)
    for f in os.listdir('tmp'):
        cmd += STREAM_PATH_TMPL.format(f)

    call(cmd.split())

def build(input_file):
    mkdir('tmp')
    vcmd = 'ffmpeg -y -i {0}'.format(input_file)
    acmd = vcmd
    streams = get_streams(input_file)

    for s in streams[0]:
      acmd += get_cmd_part(s['index'], 'audio')

    for s in streams[1]:
      vcmd += get_cmd_part(s['index'], 'video')

    p1 = Popen(acmd.split())
    p2 = Popen(vcmd.split())

    [p.wait() for p in [p1, p2]]

    segment()

if __name__ == '__main__':
    demux('media/tears_of_steel.mp4')
