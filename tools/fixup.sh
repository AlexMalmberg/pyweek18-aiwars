#!/bin/bash

name=$1

pnmscale -reduce 2 ${name}_col.ppm | pnmtopng -compression 9 > ${name}_col.png

pnmscale -reduce 2 ${name}_line.pgm \
  | pnmtopng -compression 9 \
    -alpha <(pnmscale -reduce 2 ${name}_line_alpha.pgm) \
    > ${name}_line.png
