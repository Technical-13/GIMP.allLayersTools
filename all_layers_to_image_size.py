#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from gimpfu import *
from collections import Counter

filename = "all_layers_to_image_size.py"

# Add custom library to system path
sys.path.append( os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), "libraries" ) )

# Import libraries/gimp_logger and enable_logging()
import gimp_logger
gimp_logger.enable_logging( filename )

def all_layers_to_image_size_advanced( image, drawable, fill_mode, custom_color, custom_pattern ):
    # Enable GIMP to undo this action as one single step
    gimp.context_push()
    image.undo_group_start()

    # Save the user's original environment context states to restore later
    original_bg = pdb.gimp_context_get_background()
    original_fill_mode = pdb.gimp_context_get_fill_mode()
    original_pattern = pdb.gimp_context_get_pattern()

    for layer in image.layers:
        # Avoid trying to sample or fill layer groups directly
        if pdb.gimp_item_is_group( layer ):
            continue

        # MODE 0: Auto-Detect Edge Color
        if fill_mode == 0:
            border_pixels = []
            w, h = layer.width, layer.height

            # Sample top and bottom rows
            for x in range( w ):
                _, p_top = pdb.gimp_drawable_get_pixel( layer, x, 0 )
                _, p_bot = pdb.gimp_drawable_get_pixel( layer, x, h - 1 )
                if len( p_top ) >= 3: border_pixels.append( p_top[ :3 ] )
                if len( p_bot ) >= 3: border_pixels.append( p_bot[ :3 ] )

            # Sample left and right columns (skipping corners already sampled)
            for y in range( 1, h - 1 ):
                _, p_left = pdb.gimp_drawable_get_pixel( layer, 0, y )
                _, p_right = pdb.gimp_drawable_get_pixel( layer, w - 1, y )
                if len( p_left ) >= 3: border_pixels.append( p_left[ :3 ] )
                if len( p_right ) >= 3: border_pixels.append( p_right[ :3 ] )

            # Find the most common RGB pixel tuple or default to black if empty
            if border_pixels:
                most_common_rgb = Counter( border_pixels ).most_common( 1 )[ 0 ][ 0 ]
                edge_color = gimpcolor.RGB( most_common_rgb[ 0 ], most_common_rgb[ 1 ], most_common_rgb[ 2 ] )
            else:
                edge_color = gimpcolor.RGB( 0, 0, 0 )

            # Set up selection, expand, invert, and fill with edge color
            pdb.gimp_image_select_rectangle( image, CHANNEL_OP_REPLACE, layer.offsets[ 0 ], layer.offsets[ 1 ], w, h )
            layer.resize_to_image_size()
            pdb.gimp_selection_invert( image )
            pdb.gimp_context_set_background( edge_color )
            pdb.gimp_edit_bucket_fill( layer, 1, 0, 100, 0, False, 0, 0 )

        # MODE 1: Force Transparency
        elif fill_mode == 1:
            if not pdb.gimp_drawable_has_alpha( layer ):
                pdb.gimp_layer_add_alpha( layer )
            layer.resize_to_image_size()

        # MODE 2: Pick a Color
        elif fill_mode == 2:
            w, h = layer.width, layer.height
            pdb.gimp_image_select_rectangle( image, CHANNEL_OP_REPLACE, layer.offsets[ 0 ], layer.offsets[ 1 ], w, h )
            layer.resize_to_image_size()
            pdb.gimp_selection_invert( image )
            pdb.gimp_context_set_background( custom_color )
            pdb.gimp_edit_bucket_fill( layer, 1, 0, 100, 0, False, 0, 0 ) # Fill mode 1 is BG_BUCKET_FILL

        # MODE 3: Pick a Pattern
        elif fill_mode == 3:
            w, h = layer.width, layer.height
            pdb.gimp_image_select_rectangle( image, CHANNEL_OP_REPLACE, layer.offsets[ 0 ], layer.offsets[ 1 ], w, h )
            layer.resize_to_image_size()
            pdb.gimp_selection_invert( image )
            pdb.gimp_context_set_pattern( custom_pattern )
            pdb.gimp_edit_bucket_fill( layer, 2, 0, 100, 0, False, 0, 0 ) # Fill mode 2 is PATTERN_FILL

    # Clean up: clear active selections and restore user menu environment states
    pdb.gimp_selection_none( image )
    pdb.gimp_context_set_background( original_bg )
    pdb.gimp_context_set_fill_mode( original_fill_mode )
    pdb.gimp_context_set_pattern( original_pattern )

    # Force GIMP to visually redraw the screen
    gimp.displays_flush()
    image.undo_group_end()
    gimp.context_pop()

register(
    "python_fu_all_layers_to_image_size_advanced",
    "Resize all layers and customize how the newly expanded canvas padding is filled.",
    "Resizes all layers to image size with options for edge detection matching, transparency, or pattern filling.",
    "Technical-13 / AI Assisted",
    "Public Domain",
    "2026",
    "All Layers to Image Size...",
    "*",
    [
        ( PF_IMAGE, "image", "Takes current image", None ),
        ( PF_DRAWABLE, "drawable", "Takes current layer", None ),
        ( PF_OPTION, "fill_mode", "Fill Mode:", 0, [ "Auto-detect Edge Color", "Force Transparency", "Pick Custom Color", "Pick Custom Pattern" ] ),
        ( PF_COLOR, "custom_color", "Custom Color (Mode 3):", ( 255, 255, 255 ) ),
        ( PF_PATTERN, "custom_pattern", "Custom Pattern (Mode 4):", "" )
    ],
    [],
    all_layers_to_image_size_advanced,
    menu="<Image>/Layer/All Layers" # For when there is more than just a few "All Layer" tools
    # menu="<Image>/Layer"
)

main()
