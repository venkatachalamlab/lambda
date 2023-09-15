# Motorized Stage

<p align="center">
  <img src="https://github.com/venkatachalamlab/lambda/blob/main/figures/front_view_colored.jpeg" width=800>
</p>

## Overview

The imaging system has dual parfocal scopes on opposite sides of the sample. The working distance is 2 cm for the low-magnification scope, while it's under 1 mm for the 
high-magnification scope. This configuration constrains sample accessibility during experiments. As a consequence, any apparatus used for loading or imaging the sample can't
be thicker than 2 cm. This constraint complicates the implementation of a three-dimensional moving stage. To address this issue, I adapted the design of a motorized stage developed 
in ROLI lab \cite{Kim2017} for performing panneuronal calcium imaging in freely swimming zebrafish.

In our version of the design, the stage's upper plate holding the sample connects to the bottom plate via 80-20 posts. This bottom plate is mounted on three stacked linear motors, 
enabling movements in X, Y, and Z directions. The two-level stage design left sufficient space between the plates for the low-mag scope, ensuring optimal use of the top plate area.

Given the 60x objective for imaging, it's essential to employ high-resolution motors. For the X and Y axes, I opted for the LRM200A-T3 from Zaber Technologies (discontinued as I am 
writing this report), boasting a 20 cm travel range, a minimum speed of 27 nanometers/second, and a 47nm microstep size. For vertical (Z) movement, I utilized the VSR20A-T3 from Zaber
Technologies (discontinued as I am writing this report), offering a 2 cm travel range, 58 nanometers/second speed, and 95nm microstep size.

Zaber's software development kit facilitated the seamless integration of motor controls with our main software used to control the imaging system. Both the low-mag and high-mag scopes'
images could be used for manually maneuvering the stage using an Xbox controller, in addition to a closed-loop tracking system for imaging behaving C. elegans.

To design tracking strategies, tt's important to recognize the animals' movement speed doesn't exceed 1 millimeter/second. With a 60x objective, volumetric imaging captures images 
below an 8Hz rate, covering approximately a field of view of 200 micrometers squared. Without predictive tracking algorithms, solely relying on features in the current frame  for 
tracking may cause the tracking algorithm to lose sight of the subject due to the slow imaging rate. The low-mag scope, capturing more of the imaged sample and having up to 10 times
the imaging rate of the high-mag scope, is optimal for tracking. However, this is only beneficial if the low-mag scope tracks features also visible in the high-mag scope. If, for 
instance, we track a worm's centroid, there's no assurance that the neurons of interest are within range, potentially missing crucial high-mag scope data.

The stage's design can accommodate various experiments. It features a replaceable 12-inch by 12-inch flat aluminum top plate. However, the sample's thickness shouldn't exceed 2 cm,
a limit set by the parfocality of the two scopes.

## Manual

Supplementary material on [Zaber Manuals](https://github.com/venkatachalamlab/large-files/tree/master/manuals/zaber)   
Supplementary material on [LRM200A-T3](https://github.com/venkatachalamlab/large-files/blob/master/drawings/parts_third_party/x_y_motor_lrm200_t3.pdf)  
Supplementary material on [VSR20A-T3](https://github.com/venkatachalamlab/large-files/blob/master/drawings/parts_third_party/z_motor_vsr20_t3.pdf)  
Supplementary material on [Stage Drawings](https://github.com/venkatachalamlab/large-files/tree/master/drawings/parts_stage)  
Supplementary material on [Stage Drawings](https://github.com/venkatachalamlab/large-files/tree/master/drawings/parts_stage)  

## Hardware safety limits for Zaber motors

It is possible to damage the objective if the movement in x-y plane is not limited.
To prevent this, use [Thorlabs posts](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=1266) and set safety limits for the movement in x-y plane.

You can find different sizes of these posts in the lab, stack them to make the desired length and put them inside the motors as shown in the following picture.

<p align="center">
  <img width="480" height="250" src="https://github.com/venkatachalamlab/lambda/blob/main/figures/safety_zabers.jpg">
</p>

## Maintenance

#### Corrosion
A thin layer of corrosion protectant should be applied "periodically" to all mounting surfaces. Mounting surfaces refers to the silver areas
on the carriage and the base of the stage. Boeshield T9 or WD-40 should be sprayed into a rag and wiped on all such exposed regions.

#### Lubrication
Zaber recommends re-lubricating after 500km of service. The amounts to once every 15-16 years of constant service at 1mm/s. The text/pictures below show the Zaber
manual's explanation of how to lubricate the LRM series stage.

<p align="center">
  <img width="600" height="400" src="https://github.com/venkatachalamlab/lambda/blob/main/figures/maintenance.JPG">
</p>

## Zaber console (FOR DEVELOPMENT PURPOSES ONLY)



[here](https://www.zaber.com/wiki/Software/Zaber_Console) you can find the documentation of Zaber console.
In our system, commands are directly sent to the x-y motors through a serial port.

Use this [link](https://www.zaber.com/software) to download the Zaber console.

#### Accessing a motor via Zaber console 

Motors are connected to controller boards, and controllers are connected to the computer via USB cables.
Open Zaber console and on top select the port and click on Open.

On top, you can select 'All Devices', 'Controller', 'Device axis1' or 'Device axis'

IMPORTANT: After selecting the motor, set the unit to micrometer.

<p align="center">
  <img width="525" height="415" src="https://github.com/venkatachalamlab/lambda/blob/main/figures/select_zaber.png">
</p>


#### Setting movement limits

These motors use the `reference point` and move between `limit.min` and `limit.max`. These values are stored inside the controller and there are different ways for these values
to change.

If the motor does not move, one possible reason could be inconsistencies between these values.

If for some reasons, the `reference point` is smaller than `limit.min` or larger than `limit.max` or is unknown, then the motor will not respond to move commands. 
To fix this problem use the following commands to manually change these values.

Go to the `Terminal` tab:

1. `/01 1 get pos` returns the current position for device axis 1

2. `/01 1 get limit.min` returns the limit.min for device axis 1 

3. `/01 1 set pos ###` sets the current position to ### for device axis 1

4. `/01 1 set limit.min ###` sets the limit.min to ### for device axis 1

You can use these commands to figure out what the current values for these parameters are and to change them wisely if needed.


<p align="center">
  <img width="525" height="415" src="https://github.com/venkatachalamlab/lambda/blob/main/figures/send_commands.png">
</p>

In the above picture, the user has requested for `pos`, `limit.min` and `limit.max` and at the end, the user has set the current pos to 0.
