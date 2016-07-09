import os
from subprocess import check_output, PIPE, Popen

def get_codec(trackID):
  p1 = Popen('MP4Box -info {0} media/tears_of_steel.mp4'.format(trackID).split(), stderr=PIPE)
  p2 = Popen('grep RFC6381'.split(), stdin=p1.stderr, stdout=PIPE)
  p3 = Popen(['awk', '{print $4}'], stdin=p2.stdout, stdout=PIPE)
  data, _ = p3.communicate()
  codec = data.decode('utf-8').rstrip()
  print(codec)

if __name__ == '__main__':
  trackID = 1
  get_codec(trackID)
