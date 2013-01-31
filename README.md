Project: NikCut (Maybe change name to PicSift or PicScan or PicRank)
====================
Author: Jay W Johnson

Description:
Image series comparison/ranking program that can also produce HDR images and 3D point clouds.

TODO:
    MAIN GOALS:
        -Use OpenCV's feature matching to line up multiple similar images so that specific locations can be compared in detail.
            -Image ranking uses the EXIF five star system.
        -Apply HDR algorithm to lined up images and produce a new image.
        -Apply SFM algorithm to multiple images and produce a point cloud.
    ADDITIONAL:
        -Add easy tagging feature
        -Add other simple edits
        -Manage the associated .NEF images (auto-delete low-ranked and preserve high-ranked)
            -Allow user to set different actions depending on number of stars, such as deleting .NEF, resizing, compression level.


