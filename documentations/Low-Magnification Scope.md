# Low-Magnification Inverted Scope

<p align="center">
  <img src="https://github.com/venkatachalamlab/lambda/blob/main/figures/front_view_colored.jpeg" width=800>
</p>

# Overview

The high-magnification scope has a fixed objective lens, therefore when there's a need for locating a sample, capturing the entire animal's body, or tracking behaving animals, 
a lower magnification becomes necessary. As a solution, I incorporated a secondary telecentric scope equipped with a 10x long-working-distance objective lens. This system's tube 
lens is an achromatic doublet with a focal distance of 180mm  from Thorlabs.  

To achieve parfocality between the two scopes, particularly because the high-mag scope is fixed, it's essential to be able to precisely make adjustments to the postion of the 
low magnification scope. This task is crucial since different samples might need varying adjustments due to their distinct optical properties. To address this, I employed an 
electrically tunable lens, positioned between the objective lens and tube lens of this scope. The EL-16-40-TC model from Optotune facilitates adjusting the focus of the low-mag 
scope without physically moving the objective. However, a potential drawback is that different samples might necessitate varying configurations of this lens, potentially altering 
the magnification in recordings from this scope. This is crucial when conducting tracking experiments, where there's a need to convert recording positions to real-world physical 
distances. It is important to note that the control of the tunable lens isn't integrated into the system's software, so adjustments are made manually using the Optotune software. 
The lens connects to its driver located outside the SM2 extension tubes through a USB cable.  

To align both objectives on the x-y plane, high precision translational stages are available. These stages, sourced from Thorlabs, offer a resolution of 150 micrometers per 
rotation and can be maneuvered to manually align the scopes.

A notable technical hurdle is the sub-1mm working distance of the high-mag objective. For illuminating samples for the low-mag scope, light must pass through the high-mag 
objective. This presents challenges, especially with C. elegans samples. Transmitted light microscopy offers better contrast due to the optical characteristics of 
the C. elegans body. Additionally, the small working distance of the high-mag objective and it's close distance to the sample causes the objective to appear very bright,
often brighter than the sample. This makes imaging using the low-mag scope difficult if it captures reflected light. As a remedy, we integrated Thorlab's cage cubes to 
introduce a new light path for the low-mag scope. This path serves dual purposes: as a light source for optogenetic experiments and to excite sample fluorophores for 
fluorescent imaging. However, it's worth noting that the optogenetic stimulation using this method is not targeted, illuminating the entire sample.  

Additionally, for wide-field imaging via transmitted light from the high-mag scope, I constructed a circular array of white LEDs. These LEDs are positioned around the low-mag
objective and angled to directly illuminate the sample placed in front of the objective. This lighting system is operated manually using an LED driver sourced from Thorlabs. 
It's worth mentioning that the LED driver can be onnected to a DAQ board through a BNC connector, allowing for software-based control.


# Manual 

Supplementary material on [Electrically Tunable Lens](https://github.com/venkatachalamlab/large-files/tree/master/manuals/tunable_lens)
