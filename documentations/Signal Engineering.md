# Sinal Engineering for Synchronization

## Overview

To use the output from the confocal spinning disk for system-wide synchronization, I first modify its signal. This involves converting both the falling and rising edges of the 
signal exclusively to rising edges. The modified signal, which I call the 'base signal', retains the core information from the initial confocal spinning disk signal
through its rising edges.

When counting the rising edges of this base signal, each count corresponds to a complete field of view scan by the confocal spinning disk. This relationship sets a limitation
on the camera exposure times: the exposure time must be a multiple of the full field of view scans, and this multiplier is determined by the user. Based on this count, 
I generate a new signal to control the Zyla camera's exposure. If the exposure time is set to equate to N complete scans, then this new signal will have a rising edge 
every N times a rising edge appears in the base signal. I call this new signal the 'generic trigger signal'. As Zyla operates only on the basis of rising edges, the time 
of its falling edge is inconsequential.

For the Kinetix Camera, however, the falling edge is crucial to halt the exposure. To run the Kinetix Camera, a distinct signal is generated using the generic trigger signal
and combined with the 'ready-out' signals from both Kinetix cameras. A Kinetix camera's 'ready-out' signal is high when it's prepped for a new exposure. At every rising edge
of the generic trigger, this new signal is first set low, and immediately after, it results from a logical 'and' operation between the two 'ready-out' signals. Thus, as soon 
as both cameras are ready, this signal changes to high, initiating the next exposure. I call this Kinetix-specific control signal the 'Kinetix Trigger'.

For piloting the piezo using the base signal, the positions the piezo will move to are first determined by two parameters: the number of z slices and the z resolution.
The piezo's driving signal is updated to the next calculated value each time the generic trigger signal reaches a rising edge. Termed the 'Piezo Signal', its pattern resembles
a step function that resets in sync with the volumetric imaging rate.

Lastly, the generic trigger signal also defines the lasers' states because for different volumes different combinations of the four laser lines may be needed.

<p align="center">
  <img src="https://github.com/venkatachalamlab/lambda/blob/main/figures/signals.jpeg" alt="Description of Image" width=900>
</p>
