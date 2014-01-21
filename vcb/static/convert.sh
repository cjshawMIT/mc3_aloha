#!/bin/bash
for file in *.mp4; do
    if [ ! -f ${file%%.mp4}.ogv ];
    then
      /bin/nice -n 10 ffmpeg2theora -o ${file%%.mp4}.ogv -p padma $file
    fi
done
