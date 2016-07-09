import os, json
from subprocess import check_output

SEGMENT_LENGTH = 8

def get_data(input_file):
  cmd = 'ffprobe -show_entries format:streams -v error -print_format json {0}'.format(input_file)
  res = json.loads(check_output(cmd.split()).decode('utf-8'))

  stream = res['streams'][0]
  fmt = res['format']

  bandwidth = fmt['bit_rate']
  sar = stream['sample_aspect_ratio']
  frame_rate = stream['r_frame_rate'].split('/')[0]
  width = stream['width']
  height = stream['height']
  timescale = stream['time_base'].split('/')[1]
  duration = int(timescale) * SEGMENT_LENGTH
  mime = '{0}/mp4'.format(stream['codec_type'])

  print(bandwidth, sar, frame_rate, width, height, timescale, duration, mime)


if __name__ == '__main__':
  get_data('tmp/0.mp4')
