import os, json
from subprocess import check_output, call

SEGMENT_LENGTH = 8

def transmux(source_path, playlist_type, bit_rate, segno):
    stream_index = get_stream_index(source_path, playlist_type, bit_rate)['index']
    output = os.path.join('static', playlist_type, bit_rate, '{0}.ts'.format(segno))

    cmd = 'ffmpeg -y -ss {0} -t {1} -i {2} -map 0:{3} -c copy -f mpegts {4}'
    cmd = cmd.format(SEGMENT_LENGTH * segno, SEGMENT_LENGTH, source_path, stream_index, output)
    call(cmd.split())

# TODO: extract to separate file
def get_stream_index(source_path, playlist_type, bit_rate):
    cmd = 'ffprobe -print_format json -v error -show_streams {0}'.format(source_path)
    streams = json.loads(check_output(cmd.split()))['streams']

    bit_rate_key = 'max_bit_rate' if playlist_type == 'audio' else 'bit_rate'
    return [s for s in streams if s['codec_type'] == playlist_type and s[bit_rate_key] == bit_rate][0]

if __name__ == '__main__':
    transmux('media/tears_of_steel.mp4', 'audio', '96000', 0)
