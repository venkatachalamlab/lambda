# Dragonfly 200

## Overview
Prior research utilizing confocal spinning disks has demonstrated their efficacy in recording brain activity in freely behaving C.elegans and large neuron populations
, highlighting the reliability of this method for comprehensive neuronal brain imaging. Here, we employ the Dragonfly Spinning Disk from Andor Technologies. 
Within this system, a half rotation of the disks captures the entire field of view. Operating at a peak speed of 6000rpm, the system ensures consistent illumination across
the entire field every 5 milliseconds. The system incorporates a 565nm high-pass dichroic mirror to divide incoming emitted light, directing it towards the camera sensors. 
Each camera port features a filter wheel, equipped with 8 slots. Based on my trials, transitioning from one filter to another takes about 500 milliseconds, which sets certain 
constraints on filter adjustments during imaging. The system's rotation is tracked through a TTL output signal, toggling its state with every half-disk rotation. Consequently, 
this output alternates between high and low phases, each phase duration reflecting the half-rotation time of the disks.

## Manuals
Supplementary material on [large-files repository](https://github.com/venkatachalamlab/large-files/tree/master/manuals/dragonfly)
