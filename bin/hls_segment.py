import os, json
from subprocess import check_output, call

SEGMENT_LENGTH = 8

def transmux(source_path, playlist_type, bit_rate, segno):
    stream_index = get_stream_index(source_path, playlist_type, bit_rate)['index']
    input_file = os.path.join('tmp', playlist_type, bit_rate, '{0}.ts'.format(segno))
    output_file = os.path.join('static', playlist_type, bit_rate, '{0}.ts'.format(segno))

    if playlist_type == 'video':
        cmd = 'ffmpeg -y -ss {0} -t {1} -i {2} -map 0:{3} -c:v libx264 -copyts -bsf:v h264_mp4toannexb -f mpegts -mpegts_copyts 1 {4}'
    else:
        cmd = 'ffmpeg -y -ss {0} -t {1} -i {2} -map 0:{3} -c:a copy -copyts -f mpegts -mpegts_copyts 1 {4}'

    cmd = cmd.format(SEGMENT_LENGTH * segno, SEGMENT_LENGTH, source_path, stream_index, output_file)
    call(cmd.split())

# TODO: extract to separate file
def get_stream_index(source_path, playlist_type, bit_rate):
    cmd = 'ffprobe -print_format json -v error -show_streams {0}'.format(source_path)
    streams = json.loads(check_output(cmd.split()).decode('utf-8'))['streams']
    return [s for s in streams if s['codec_type'] == playlist_type and s['bit_rate'] == bit_rate][0]

if __name__ == '__main__':
    transmux('media/tears_of_steel.mp4', 'audio', '96000', 0)
