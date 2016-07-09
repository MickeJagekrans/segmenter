#!/usr/bin/env python3

import os, json

from subprocess import check_output, PIPE, Popen
from lxml import etree
from datetime import datetime

SEGMENT_LENGTH = 8

def sort_streams(streams, stream_type):
    return sorted([s for s in streams if s['codec_type'] == stream_type], key=lambda k: int(k['bit_rate']), reverse=True)

def get_codecs(input_file):
    p1 = Popen('MP4Box -info {0}'.format(input_file).split(), stderr=PIPE)
    p2 = Popen('grep RFC6381'.split(), stdin=p1.stderr, stdout=PIPE)
    p3 = Popen(['awk', '{print $4}'], stdin=p2.stdout, stdout=PIPE)
    data, _ = p3.communicate()
    codecs = data.decode('utf-8').rstrip()
    return codecs.split('\n')

def get_data(input_file):
    cmd = 'ffprobe -show_entries format:streams -v error -print_format json {0}'.format(input_file)
    data = json.loads(check_output(cmd.split()).decode('utf-8'))
    streams = data['streams']
    audio = sort_streams(streams, 'audio')
    video = sort_streams(streams, 'video')
    return (data['format'], audio, video)

def build_video_representation(fmt, stream, codecs):
    idx = stream['index']

    representation = etree.Element(
        'Representation',
        id=str(idx),
        mimeType='{0}/mp4'.format(stream['codec_type']),
        codecs=codecs[int(idx)],
        width=str(stream['width']),
        height=str(stream['height']),
        frameRate=stream['r_frame_rate'].split('/')[0],
        sar=stream['sample_aspect_ratio'],
        startWithSAP='1',
        bandwidth=str(stream['bit_rate'])
    )

    timescale = stream['time_base'].split('/')[1]

    etree.SubElement(
        representation,
        'SegmentTemplate',
        timescale=timescale,
        media='seg_{0}$Number$.m4s'.format(idx),
        startNumber='1',
        duration=str(int(timescale) * SEGMENT_LENGTH)
    )

    return representation

def build_audio_representation(fmt, stream, codecs):
    idx = stream['index']

    representation = etree.Element(
        'Representation',
        id=str(idx),
        mimeType='{0}/mp4'.format(stream['codec_type']),
        codecs=codecs[int(idx)],
        audioSamplingRate=str(stream['sample_rate']),
        startWithSAP='1',
        bandwidth=str(stream['bit_rate'])
    )

    timescale=stream['time_base'].split('/')[1]

    etree.SubElement(
        representation,
        'SegmentTemplate',
        media='seg_{0}$Number$.m4s',
        timescale=timescale,
        startNumber="1",
        duration=str(int(timescale) * SEGMENT_LENGTH)
    )

    return representation

def build_mpd(input_file):
    data = get_data(input_file)
    codecs = get_codecs(input_file)

    duration_time = datetime.fromtimestamp(float(data[0]['duration'])).time()

    h = duration_time.hour
    m = duration_time.minute
    s = "{0}.{1}".format(duration_time.second, duration_time.microsecond // 1000)

    duration = 'PT{0}H{1}M{2}S'.format(h, m, s)

    root = etree.Element(
        'MPD',
        xmlns='urn:mpeg:dash:schema:mpd:2011',
        minBufferTime='PT1.500S',
        type="static",
        mediaPresentationDuration=duration,
        maxSegmentDuration='PT0H0M{0}.000S'.format(SEGMENT_LENGTH),
        profiles='urn:mpeg:dash:profile:full:2011'
    )

    period = etree.SubElement(
        root,
        'Period',
        duration=duration
    )

    first_video = data[2][0]

    video_adaptation_set = etree.SubElement(
        period,
        'AdaptationSet',
        segmentAlignment='true',
        bitstreamSwitching='true',
        maxWidth=str(first_video['width']),
        maxHeight=str(first_video['height']),
        maxFrameRate=first_video['r_frame_rate'].split('/')[0],
        par='{0}:{1}'.format(first_video['width'], first_video['height']),
        lang=first_video['tags']['language']
    )

    etree.SubElement(
        video_adaptation_set,
        'SegmentTemplate',
        initialization='Manifest_set1_init.mp4'
    )

    fmt = data[0]

    for entry in data[2]:
        video_adaptation_set.append(build_video_representation(fmt, entry, codecs))

    first_audio = data[1][0]

    audio_adaptation_set = etree.SubElement(
        period,
        'AdaptationSet',
        segmentAlignment='true',
        bitstreamSwitching='true',
        lang=first_audio['tags']['language']
    )

    etree.SubElement(
        audio_adaptation_set,
        'AudioChannelConfiguration',
        schemeIdUri="urn:mpeg:dash:23003:3:audio_channel_configuration:2011",
        value=str(first_audio['channels'])
    )

    etree.SubElement(
        audio_adaptation_set,
        'SegmentTemplate',
        initialization='Manifest_set2_init.mp4'
    )

    for entry in data[1]:
        audio_adaptation_set.append(build_audio_representation(fmt, entry, codecs))

    print(etree.tostring(root, pretty_print=True, xml_declaration = True, encoding='UTF-8').decode('utf-8'))

if __name__ == '__main__':
    build_mpd('media/tears_of_steel.mp4')
