#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *

def all_layers_to_image_size(image, drawable):
    # Enable GIMP to undo this action as one single step
    gimp.context_push()
    image.undo_group_start()
    
    # Loop through all layers and resize them
    for layer in image.layers:
        layer.resize_to_image_size()
        
    # Force GIMP to visually redraw the screen
    gimp.displays_flush()
    
    image.undo_group_end()
    gimp.context_pop()

register(
    "python_fu_all_layers_to_image_size",
    "Resize all layers to match the image canvas boundaries.",
    "Resizes all layers to image size simultaneously.",
    "Technical-13 / AI Assisted",
    "Public Domain",
    "2026",
    "All Layers to Image Size",
    "*", # Works on any type of image (RGB, Grayscale, etc.)
    [
        (PF_IMAGE, "image", "Takes current image", None),
        (PF_DRAWABLE, "drawable", "Takes current layer", None),
    ],
    [],
    all_layers_to_image_size,
    menu="<Image>/Layer" # This places it directly inside the 'Layer' menu
)

main()
