import argparse
import datetime
import json
import logging
import os
import sys
import time

import xml.etree.cElementTree as ET
import xml.dom.minidom

"""
VRTP format:

{   "header":
	{
		"colour":-16777216,
		"name":"T12 A1",
		"lastModTime":1606135298501,
		"trackId":"11699434",
		"gridPositionCoordType":17
	},
	"points":
	[
        {"lat":28.397722,"lon":-16.585778,"map_x":-139131590,"map_y":248615801,"alt":119.16730730796871,"time":1623343518329}

Above json is unterminated

We want to get it into GPX, we will grab:
    header.name
    points.*.{lat, lon, time}

- time (if available) is epoch.
- alt is optional (routes vs tracks)


VRTP lives in `Android/data/com.augmentra.viewranger.android/files/viewrangermoved/Tracks`
"""

def validate_file(f):
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f


def load_vrtp(path):
    with open(path, encoding='utf-8', mode='r') as file:
        data = file.read()
    try:
        j = json.loads(data)
    except:
        data += ']}'
        j = json.loads(data)
    return j


def vrtp_to_gpx(j: json):
    name = j['header']['name']
    root = ET.Element("gpx", {'version': '1.0'})
    ET.SubElement(root, 'name').text = name

    had_alt = False
    had_time = False

    trk = ET.SubElement(root, 'trk')
    ET.SubElement(trk, 'name').text = name
    ET.SubElement(trk, 'number').text = '1'
    seg = ET.SubElement(trk, 'trkseg')
    for p in j['points']:
        trkpt = ET.SubElement(seg, 'trkpt', {'lat': str(p['lat']), 'lon': str(p['lon'])})
        if 'alt' in p and p['alt'] != 0.0:
            had_alt = True
            ET.SubElement(trkpt, 'ele').text = str(p['alt'])
        t = p['time']
        if t == 0:
            t = int(time.time())
        else:
            had_time = True
            t = t / 1000
        ET.SubElement(trkpt, 'time').text = datetime.datetime.utcfromtimestamp(t).isoformat()

    logging.debug(f'Found altitude: {had_alt}')
    logging.debug(f'Found time    : {had_time}')

    dom = xml.dom.minidom.parseString(ET.tostring(root))
    gpx = dom.toprettyxml()
    return gpx


def write_gpx(output, gpx):
    with open(output, 'w') as file:
        file.write(gpx)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--input', dest='input', required=True, type=validate_file, help='input vrtp file', metavar='FILE')
    p.add_argument('-d', '--debug', action='store_true')
    args = p.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    j = load_vrtp(args.input)

    gpx = vrtp_to_gpx(j)

    output = args.input + '.gpx'
    logging.info(f'Will write output to: {output}')

    write_gpx(output, gpx)

    return 0

if __name__ == '__main__':
    sys.exit(main())
