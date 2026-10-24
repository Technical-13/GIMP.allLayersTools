#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from gimpfu import *
from collections import Counter

filename = "all_layers_fuzzy_delete_at_point.py"

# Add custom library to system path
sys.path.append( os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), "libraries" ) )

# Import libraries/gimp_logger and enable_logging()
import gimp_logger
gimp_logger.enable_logging( filename )

def all_layers_fuzzy_delete_advanced( image, drawable, threshold, select_transparent ):
    gimp.context_push()
    image.undo_group_start()

    # Get the coordinates from the 1x1 pixel selection.
    has_selection, x1, y1, x2, y2 = pdb.gimp_selection_bounds( image )

    if not has_selection:
        gimp.message( "Please select a 1x1 pixel on the canvas first." )
        return

    if ( x2 - x1 ) != 1 or ( y2 - y1 ) != 1:
        gimp.message( "Please make a 1x1 pixel selection first." )
        return

    click_x, click_y = x1, y1

    for layer in image.layers:
        if pdb.gimp_item_is_group( layer ):
            continue

        if not pdb.gimp_drawable_has_alpha( layer ):
            pdb.gimp_layer_add_alpha( layer )

        # Run Fuzzy Select on the grabbed coordinates for this isolated layer frame
        pdb.gimp_image_select_fuzzy(
            image,
            0, # CHANNEL_OP_REPLACE
            layer,
            click_x,
            click_y,
            threshold,
            False,
            True,
            False,
            0,
            select_transparent
        )

        # Delete the selected background region instantly
        pdb.gimp_edit_clear( layer )

    # Clean up canvas selection lines
    pdb.gimp_selection_none( image )
    gimp.displays_flush()

    image.undo_group_end()
    gimp.context_pop()

register(
    "python_fu_all_layers_fuzzy_delete_advanced",
    "Fuzzy select and delete pixels at an interactively picked canvas coordinate across all layers.",
    "Grabs a coordinate via a canvas click picker, runs a Magic Wand selection loop, and deletes matching spaces.",
    "Technical-13 / AI Assisted",
    "Public Domain",
    "2026",
    "Fuzzy Delete at Selected Point...",
    "*",
    [
        ( PF_IMAGE, "image", "Takes current image", None ),
        ( PF_DRAWABLE, "drawable", "Takes current layer", None ),
        ( PF_SLIDER, "threshold", "Fuzzy Select Threshold:", 15, ( 0, 255, 1 ) ),
        ( PF_TOGGLE, "select_transparent", "Select Transparent Regions:", False )
    ],
    [],
    all_layers_fuzzy_delete_advanced,
    menu="<Image>/Layer/All Layers" # For when there is more than just a few "All Layer" tools
    # menu="<Image>/Layer"
)

main()
