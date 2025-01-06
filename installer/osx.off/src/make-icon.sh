#!/bin/bash

rm -rf image.iconset
mkdir image.iconset
rsvg-convert -h 16 $1 > image.iconset/icon_16x16.png
rsvg-convert -h 32 $1 > image.iconset/icon_16x16@2x.png
rsvg-convert -h 32 $1 > image.iconset/icon_32x32.png
rsvg-convert -h 64 $1 > image.iconset/icon_32x32@2x.png
rsvg-convert -h 128 $1 > image.iconset/icon_128x128.png
rsvg-convert -h 256 $1 > image.iconset/icon_128x128@2x.png
rsvg-convert -h 256 $1 > image.iconset/icon_256x256.png
rsvg-convert -h 512 $1 > image.iconset/icon_256x256@2x.png
rsvg-convert -h 512 $1 > image.iconset/icon_512x512.png
rsvg-convert -h 1024 $1 > image.iconset/icon_512x512@2x.png
iconutil -c icns image.iconset
rm -R image.iconset
