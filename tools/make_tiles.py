import ctypes
import math
import random
from scipy import interpolate


# All tiles arranged to go counter-clockwise around land.


Water = (132, 161, 255)
Land = (255, 205, 86)

Size = 64
Offset = 16
Brush = 4


def Line(t):
  return (t * Size, Offset)

def LineNormal(t):
  return (0, 1)


def OutsideCircle(t):
  t = t * math.pi / 2.
  w = Size - Offset
  return (Size - math.cos(t) * w, Size - math.sin(t) * w)

def OutsideCircleNormal(t):
  t = t * math.pi / 2.
  w = Size - Offset
  return (-math.cos(t), math.sin(t))


def InsideCircle(t):
  t = t * math.pi / 2.
  w = Offset
  return (math.sin(t) * w, math.cos(t) * w)

def InsideCircleNormal(t):
  t = t * math.pi / 2.
  w = Offset
  return (-math.sin(t), math.cos(t))


def SetPixel(img, x, y, t):
  if x < 0 or x >= Size or y < 0 or y >= Size:
    return
  if not img[y * Size + x]:
    img[y * Size + x] = t


def BrushAt(img, x, y, brush, t):
  x = int(round(x))
  y = int(round(y))

  for dx in xrange(-brush, brush + 1):
    for dy in xrange(-brush, brush + 1):
      if dx * dx + dy * dy > brush * brush:
        continue
      SetPixel(img, x + dx, y + dy, t)


Subdivs = 8

def MakeTile(func, normal):
  ts = []
  ts.append(0)

  dt = 1. / (Subdivs + 2)
  for i in xrange(1, Subdivs):
    ii = i + 1
    t = random.uniform(ii * dt - dt * 0.4, ii * dt + dt * 0.4)
    ts.append(t)

  ts.append(1)
  #print ' '.join(['%4.2f' % t for t in ts])

  base_points = [func(t) for t in ts]
  normal = [normal(t) for t in ts]

  xs = []
  ys = []
  xs.append(base_points[0][0])
  ys.append(base_points[0][1])
  for i in xrange(1, Subdivs):
    ofs = random.normalvariate(0, Size * 0.02)
    xs.append(base_points[i][0] + ofs * normal[i][0])
    ys.append(base_points[i][1] + ofs * normal[i][1])

  xs.append(base_points[-1][0])
  ys.append(base_points[-1][1])

  final_x = interpolate.interp1d(ts, xs, kind='cubic')
  final_y = interpolate.interp1d(ts, ys, kind='cubic')

  image = (ctypes.c_ubyte * (Size * Size))()
  line = (ctypes.c_ubyte * (Size * Size))()
  line_alpha = (ctypes.c_ubyte * (Size * Size))()
  steps = Size * 4
  for i in xrange(steps + 1):
    t = i / float(steps)
    p = (final_x(t), final_y(t))
    BrushAt(image, p[0], p[1], Brush, 1)
    BrushAt(line_alpha, p[0], p[1], Brush, 255)

  for b in xrange(1, int(Brush * 2.5)):
    for i in xrange(steps + 1):
      t = i / float(steps)
      p = (final_x(t), final_y(t))
      BrushAt(line, p[0], p[1], b, int(255.0 * t))

  return image, line, line_alpha


def FloodFill(col, img, x, y):
  q = set()
  q.add((x, y))
  done = set()
  while q:
    x, y = q.pop()
    done.add((x, y))
    if img[y * Size + x]:
      continue
    col[(y * Size + x) * 3 + 0] = Land[0]
    col[(y * Size + x) * 3 + 1] = Land[1]
    col[(y * Size + x) * 3 + 2] = Land[2]

    def MaybePush(x, y):
      if x < 0 or x >= Size or y < 0 or y >= Size:
        return
      if (x, y) not in done:
        q.add((x, y))

    MaybePush(x - 1, y)
    MaybePush(x + 1, y)
    MaybePush(x, y - 1)
    MaybePush(x, y + 1)


def Color(img):
  col = (ctypes.c_ubyte * (Size * Size * 3))()
  for y in xrange(Size):
    for x in xrange(Size):
      if img[y * Size + x]:
        col[(y * Size + x) * 3 + 0] = 0
        col[(y * Size + x) * 3 + 1] = 0
        col[(y * Size + x) * 3 + 2] = 0
      else:
        col[(y * Size + x) * 3 + 0] = Water[0]
        col[(y * Size + x) * 3 + 1] = Water[1]
        col[(y * Size + x) * 3 + 2] = Water[2]
  FloodFill(col, img, 0, 0)
  return col


def MakeFullTile(name, func, nfunc):
  print 'Make %s...' % name
  img, line, line_alpha = MakeTile(func, nfunc)
  col = Color(img)
  with open(name + '_col.ppm', 'wb') as f:
    f.write('P6 %i %i 255\n' % (Size, Size))
    f.write(col)
  with open(name + '_line.pgm', 'wb') as f:
    f.write('P5 %i %i 255\n' % (Size, Size))
    f.write(line)
  with open(name + '_line_alpha.pgm', 'wb') as f:
    f.write('P5 %i %i 255\n' % (Size, Size))
    f.write(line_alpha)


def main():
  for i in xrange(16):
    MakeFullTile('line%02i' % i, Line, LineNormal)

  for i in xrange(16):
    MakeFullTile('ic%02i' % i, InsideCircle, InsideCircleNormal)

  for i in xrange(16):
    MakeFullTile('oc%02i' % i, OutsideCircle, OutsideCircleNormal)


if __name__ == '__main__':
  main()


"""
Tiles:
  Line
  Inside circle
  Outside circle
  Solid land
  Solid water
"""
