import os, json
from subprocess import check_output, call

SEGMENT_LENGTH = 8

def segment(source_path, playlist_type, bit_rate):
    stream_index = get_stream_index(source_path, playlist_type, bit_rate)['index']
    output_file = os.path.join('static', playlist_type, bit_rate, '%d.ts')

    if playlist_type == 'video':
        cmd = 'ffmpeg -y -i {0} -map 0:{1} -c:v copy -bsf:v h264_mp4toannexb -f ssegment -segment_time {2} {3}'
    else:
        cmd = 'ffmpeg -y -i {0} -map 0:{1} -c:a copy -f ssegment -segment_time {2} {3}'

    cmd = cmd.format(source_path, stream_index,  SEGMENT_LENGTH, output_file)
    call(cmd.split())

# TODO: extract to separate file
def get_stream_index(source_path, playlist_type, bit_rate):
    cmd = 'ffprobe -print_format json -v error -show_streams {0}'.format(source_path)
    streams = json.loads(check_output(cmd.split()).decode('utf-8'))['streams']
    return [s for s in streams if s['codec_type'] == playlist_type and s['bit_rate'] == bit_rate][0]

if __name__ == '__main__':
    transmux('media/tears_of_steel.mp4', 'audio', '96000', 0)
