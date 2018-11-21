#!/usr/bin/python
import math

start_ref = 2
radius = 50
page_height = 210
page_width = 297

polys = [
  {"name": "4-Way", "sides": 4},
  {"name": "5-Way", "sides": 5},
  {"name": "7-Way", "sides": 7},
]

edge_parts = [
  [3,0],
  [0.8,0],
  [0.8,12],
  [-0.8,12],
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
  for i in range(1, poly["sides"]):
    start_ref += 1
    theta = (((2*math.pi)/poly["sides"])*i+(math.pi/2))%(2*math.pi)
    generate_footprint(theta, start_ref, poly["name"])

angles = edges.keys()
angles.sort()
last = edges[angles[-1]][-1]
for angle in angles:
  point = edges[angle][0]
  point[0] = float("{:.2f}".format(point[0]))
  point[1] = float("{:.2f}".format(point[1]))
  theta = abs(math.degrees(math.atan2(point[1]-dy, point[0]-dx)-math.atan2(last[1]-dy, last[0]-dx)))
  dynamic += "  (gr_arc (start {:.2f} {:.2f}) (end {:.8f} {:.8f}) (angle {:.8f}) (layer Edge.Cuts) (width 0.05))\n".format(dx, dy, point[0], point[1], theta)
  last = point
  for point in edges[angle][1:]:
    dynamic += "  (gr_line (start {:.2f} {:.2f}) (end {:.2f} {:.2f}) (layer Edge.Cuts) (width 0.05))\n".format(last[0], last[1], point[0], point[1])
    last = point

with open("../geodesic.kicad_pcb", "w") as FILE:
  FILE.write(template.replace("{dynamic}", dynamic))
