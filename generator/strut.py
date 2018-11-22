#!/usr/bin/python
import math

radius = 60
dome_radius = 500
page_height = 297
page_width = 420
#length = 261.9
#angle = math.radians(15.18)
length = 357.4
angle = math.radians(20.94)
paths = [
  "/5BF6C278",
  "/5BFD12AE"
]

edge_parts = [
  [-10, -17],
  [-0.8, -17],
  [-0.8, -14],
  [-1.8, -12],
  [1.8, -12],
  [0.8, -14],
  [0.8, -17],
  [10, -17],
]
edges = {}

dynamic = ""
dx = float("{:.2f}".format(page_width/2))
dy = float("{:.2f}".format(page_height/2))

with open("./strut_connector.txt", "r") as FILE:
  footprint = FILE.read()
with open("./strut_main.txt", "r") as FILE:
  template = FILE.read()

def generate_footprint(theta,x,ref,val,path,flip=False):
  global dynamic
  y = dy
  r = (270-theta/math.pi*180)%360
  ntheta = theta+math.pi/2
  edges[r] = [
    [
      point[0]*math.cos(ntheta)-point[1]*math.sin(ntheta)+x,
      point[0]*math.sin(ntheta)+point[1]*math.cos(ntheta)+y
    ] for point in edge_parts
  ]
  new_fp= footprint.format(x=x,y=y,r=r,ref=ref,val=val,r2=r+90,path=path)+"\n"
  if flip:
    new_fp = new_fp.replace("B.", "temp.")
    new_fp = new_fp.replace("F.", "B.")
    new_fp = new_fp.replace("temp.", "F.")
    new_fp = new_fp.replace("(at ", "OTHERSENT", 1)
    new_fp = new_fp.replace("(at -", "SENTINEL")
    new_fp = new_fp.replace("(at ", "(at -")
    new_fp = new_fp.replace("SENTINEL", "(at ")
    new_fp = new_fp.replace("OTHERSENT", "(at ")
  dynamic += new_fp

generate_footprint(math.pi-angle,dx-(length-radius*2)/2,"J1","Left",paths[0],flip=True)
generate_footprint(angle,dx+(length-radius*2)/2,"J2","Right",paths[1])

def approx_arc(cx, cy, lx, ly, theta, last, segments=100):
  string = ""
  start_theta = math.atan2(ly-cy, lx-cx)
  radius = math.sqrt((ly-cy)**2+(lx-cx)**2)
  for seg in range(segments):
    ct = start_theta + (math.radians(theta)/segments)*seg
    x = radius*math.cos(ct)+cx
    y = radius*math.sin(ct)+cy
    string += "  (gr_line (start {:.2f} {:.2f}) (end {:.2f} {:.2f}) (layer Edge.Cuts) (width 0.05))\n".format(lx, ly, x, y)
    lx = x
    ly = y
  return string, [lx, ly]

angles = edges.keys()
angles.sort()
last = edges[angles[-1]][-1]
for angle in angles:
  print(angle)
  point = edges[angle][0]
  point[0] = float("{:.2f}".format(point[0]))
  point[1] = float("{:.2f}".format(point[1]))
  x = length
  y = math.sqrt(abs(dome_radius**2-x**2))
  center = [
    dx,
    dy+y
  ]
  print(point, last)
  theta = -1*math.degrees(math.atan2(point[1]-center[1], point[0]-center[0])-math.atan2(last[1]-center[1], last[0]-center[0]))
  lines, npoint = approx_arc(center[0], center[1], point[0], point[1], theta, last)
  dynamic += lines
#  dynamic += "  (gr_arc (start {:.2f} {:.2f}) (end {:.8f} {:.8f}) (angle {:.8f}) (layer Edge.Cuts) (width 0.05))\n".format(center[0], center[1], point[0], point[1], theta)
  dynamic += "  (gr_line (start {:.2f} {:.2f}) (end {:.2f} {:.2f}) (layer Edge.Cuts) (width 0.05))\n".format(last[0], last[1], npoint[0], npoint[1])
  last = point
  for point in edges[angle]:
    dynamic += "  (gr_line (start {:.2f} {:.2f}) (end {:.2f} {:.2f}) (layer Edge.Cuts) (width 0.05))\n".format(last[0], last[1], point[0], point[1])
    last = point

with open("../strut.kicad_pcb", "w") as FILE:
  FILE.write(template.replace("{dynamic}", dynamic))
