import os, json
from subprocess import Popen, check_output, call

STREAM_PATH_TMPL = ' tmp/{0}'

def get_codec_type(input_file, index):
    cmd = 'ffprobe -v quiet -show_entries stream=codec_type -select_streams {0} -print_format json {1}'.format(index, input_file)
    data = json.loads(check_output(cmd.split()).decode('utf-8'))

    print(data['streams'][0]['codec_type'])

    return data['streams'][0]['codec_type']

def get_cmd_part(idx, codec_type):
    return ' -map 0:{0} -c copy tmp/{0}.{1}'.format(idx, ext)

def segment(index, source_path):
    mpd_path = os.path.join('static', 'dash', '{0}.mpd'.format(index))
    cmd = 'MP4Box -dash 8000 -frag 8000 -rap -segment-name seg_%s_ -url-template -out {0} {1}'.format(mpd_path, source_path)
    call(cmd.split())

def build(input_file, index):
    codec_type = get_codec_type(input_file, index)
    ext = 'mp4' if codec_type == 'video' else 'm4a'
    out_path = 'tmp/{0}.{1}'.format(index, ext)
    cmd = 'ffmpeg -y -i {0} -map 0:{1} -c copy {2}'.format(input_file, index, out_path)
    call(cmd.split())

    segment(index, out_path)

if __name__ == '__main__':
    build('media/tears_of_steel.mp4', 0)
