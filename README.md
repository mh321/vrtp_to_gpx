Sadly Viewranger had been decommed. Your tracks are still in your device and it is possible to convert them from a proprietary format into more palatable GPX format.

## Where are my tracks?
Look at a location similar to this in your device: `Android/data/com.augmentra.viewranger.android/files/viewrangermoved/Tracks`. You are looking for files named something like `Track1.vrtp`.

## Transformation
```
$ python3 ./convert.py -d -i Track227.vrtp
DEBUG:root:Found altitude: True
DEBUG:root:Found time    : True
INFO:root:Will write output to: Track227.vrtp.gpx
```

## Batch transformation
```
$ find . -name \*.vrtp -type f -exec python3 ./convert.py -d -i {} \
```

## Details

### VRTP format
```json
{
  "header":
  {
    "colour":-16777216,
    "name":"Track Jun 10, 2021 17:44:45",
    "lastModTime":1606135298501,
    "trackId":"11699434",
    "gridPositionCoordType":17
  },
  "points":
    [
      {"lat":28.397722,"lon":-16.585778,"map_x":-139131590,"map_y":248615801,"alt":119.16730730796871,"time":1623343518329}
...
```

VRTP file is not a proper JSON file as the points array is unterminated.

We want to get it into GPX, we will grab:
- `header.name`
- `points.*.{lat, lon, time}`
- `time` (if available) is epoch.
- `alt` is optional (your recorded tracks will have altitude)

### GPX format

We want to transform above into something like:

```xml
<?xml version="1.0" ?>
<gpx version="1.0">
        <name>Track Jun 10, 2021 17:44:45</name>
        <trk>
                <name>Track Jun 10, 2021 17:44:45</name>
                <number>1</number>
                <trkseg>
                        <trkpt lat="28.397831" lon="-16.585489">
                                <ele>116.75174371687501</ele>
                                <time>2021-06-10T16:44:45.329000</time>
                        </trkpt>
...
```

