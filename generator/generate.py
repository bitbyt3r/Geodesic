#!/usr/bin/python
import math

start_ref = 2
radius = 65
page_height = 210
page_width = 297

polys = [
  {"name": "Hexagon", "sides": 6},
  {"name": "Pentagon", "sides": 5}
]

edge_parts = [
  [6.5,0],
  [0.8,0],
  [0.8,12],
  [-0.8,12],
  [-0.8,0],
  [-6.5,0],
]
edges = {}

dynamic = ""

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
  for point in edges[angle]:
    dynamic += "  (gr_line (start {:.2f} {:.2f}) (end {:.2f} {:.2f}) (layer Edge.Cuts) (width 0.05))".format(last[0], last[1], point[0], point[1])+"\n"
    last = point

with open("../geodesic.kicad_pcb", "w") as FILE:
  FILE.write(template.replace("{dynamic}", dynamic))
