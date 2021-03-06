#!/usr/bin/python
import math

start_ref = 2
radius = 60
page_height = 210
page_width = 297

polys = [
  {"name": "4-Way", "sides": [90, 180, 270]},
  {"name": "7-Way", "sides": [49.21, 113.95, 163.16, 212.37, 261.58, 310.79]},
]

edge_parts = [
  [3,0],
  [0.8,0],
  [0.8,10],
  [2,12],
  [-2,12],
  [-0.8,10],
  [-0.8,0],
  [-3,0],
]
edges = {}

dynamic = ""
dx = float("{:.2f}".format(page_width/2))
dy = float("{:.2f}".format(page_height/2))

with open("./template.txt", "r") as FILE:
  footprint = FILE.read()
with open("./main.txt", "r") as FILE:
  template = FILE.read()

def generate_footprint(theta,ref,val):
  global dynamic
  x = radius*math.cos(theta)+page_width/2
  y = radius*math.sin(theta)+page_height/2
  r = (90-theta/math.pi*180)%360
  ntheta = theta+math.pi/2
  edges[r] = [
    [
      point[0]*math.cos(ntheta)-point[1]*math.sin(ntheta)+x,
      point[0]*math.sin(ntheta)+point[1]*math.cos(ntheta)+y
    ] for point in edge_parts
  ]
  dynamic += footprint.format(x=x,y=y,r=r,ref=ref,val=val,r2=r+90)+"\n"

generate_footprint(math.pi/2,"J{0}".format(start_ref),"Base")
for poly in polys:
  for side in poly["sides"]:
    start_ref += 1
    theta = (math.radians(side)+(math.pi/2))%(2*math.pi)
    generate_footprint(theta, start_ref, poly["name"])

def approx_arc(cx, cy, lx, ly, theta, segments=100):
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
  point = edges[angle][0]
  point[0] = float("{:.2f}".format(point[0]))
  point[1] = float("{:.2f}".format(point[1]))
  theta = abs(math.degrees(math.atan2(point[1]-dy, point[0]-dx)-math.atan2(last[1]-dy, last[0]-dx)))
#  dynamic += "  (gr_arc (start {:.2f} {:.2f}) (end {:.8f} {:.8f}) (angle {:.8f}) (layer Edge.Cuts) (width 0.05))\n".format(dx, dy, point[0], point[1], theta)
  lines, npoint = approx_arc(dx, dy, point[0], point[1], theta)
  dynamic += lines
  dynamic += "  (gr_line (start {:.2f} {:.2f}) (end {:.2f} {:.2f}) (layer Edge.Cuts) (width 0.05))\n".format(last[0], last[1], npoint[0], npoint[1])
  last = point
  for point in edges[angle][1:]:
    dynamic += "  (gr_line (start {:.2f} {:.2f}) (end {:.2f} {:.2f}) (layer Edge.Cuts) (width 0.05))\n".format(last[0], last[1], point[0], point[1])
    last = point

with open("../geodesic.kicad_pcb", "w") as FILE:
  FILE.write(template.replace("{dynamic}", dynamic))
