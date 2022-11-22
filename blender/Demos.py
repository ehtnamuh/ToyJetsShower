import bpy
import numpy as np
import json
from math import radians
import pathlib
import os


def create_sphere(location, scale = 0.01):
    # create cube
    location = scale*np.array(location) 
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.01, calc_uvs=False, enter_editmode=False, align='WORLD', location=(0.0, location[0], location[1]), rotation=(0.0, 0.0, 0.0), scale=(1, 1, 1))

# Traverse Tree1
def traverse_tree(tree, content, i, parent = [-1,-1]):
    if( tree[i][0] == tree[i][1] == -1):
        new_momentum = np.array(content[i]) + np.array(parent)
        create_sphere(new_momentum, scale = 0.01)
        return
    # plot content
    new_momentum  = np.array(content[i])*0.2 + np.array(parent) 
    # setting root to 0
    if( parent[0]==parent[1]==-1):
        new_momentum = np.array([0,0])
    create_sphere(new_momentum, scale = 0.01)
    traverse_tree(tree, content, tree[i][0], new_momentum ) # left child
    traverse_tree(tree, content, tree[i][1], new_momentum ) # right child


with open("test.json") as f:
    data = json.load(f)
print(len(data["content"]))
traverse_tree(data["tree"],data["content"],0)

#"C:\\Users\samin\OneDrive\Desktop\CERN\ToyJetsShower\blender\data\test.json"