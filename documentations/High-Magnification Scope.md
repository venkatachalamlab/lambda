# High-Magnification Upright Scope

<div style="display: flex; justify-content: space-around; align-items: center;">
    <figure>
        <img src="https://github.com/venkatachalamlab/lambda/blob/main/figures/tube_lens.jpg" alt="image" height="200"/>
        <figcaption> SWTLU-C </figcaption>
    </figure>
    <figure>
        <img src="https://github.com/venkatachalamlab/lambda/blob/main/figures/piezo.png" alt="image" height="200"/>
        <figcaption> FOCHS.100 </figcaption>
    </figure>
    <!-- Add more figures as needed -->
</div>


## Overview 

To capture neuronal activity, I constructed a telecentric scope utilizing an SWTLU-C tube lens by Olympus with a 180mm focal length and a large 26.5mm field of view, in conjunction with a high-magnification objective.
Initially, I employed a 40x oil immersion objective, but it proved suboptimal for capturing volumetric images of biological specimens. Volumetric imaging requires capturing images of 
the same specimen at various depths, but with the oil immersion objective, the brightness of the signal significantly diminishes as the imaging depth increases. Moreover, the animal's 
head only filled a small fraction of the entire field of view when using the 40x objective, hinting at the potential to amplify the magnification. When the specimen fills the field of 
view, this enhancement has dual benefits: it increases the resolution and results in the collection of more light from the same neurons. Due to these reasons, I transitioned to a 60x 
silicone immersion objective. This is superior for imaging at varying depths as the signal's brightness decays at a more gradual rate with increasing depth.

For Z scanning, I incorporated the FOCHS.100 by Piezoconcept, which offers a precise 0.1 nm resolution and a travel range of 100 micrometers—surpassing the thickness of an adult
c. elegans. My evaluations indicated that the piezo can shift by 2 micrometers in under 200 nanoseconds, making it an excellent choice for fast Z scanning. The piezo's position can
be controlled via an external analog voltage ranging from 0 V to 10 V, enabling adjustments from 0 micrometers up to 100 micrometers.

To assemble the scope, I utilized the SM2 cage system and SM2 extension tubes by Thorlabs. The tube lens featured an M41 x 0.5 mm mounting thread. To ensure its compatibility with
my setup, I designed an adapter that transitioned from internal M41 x 0.5 mm threads to external SM2 threads.

Lastly, a 45-degree mirror positioned after the tube lens directs the light beams towards the 4f extension box, which bridges the high-magnification scope to the confocal spinning disk.

## Manual
Supplementary material on [tube lens](https://github.com/venkatachalamlab/large-files/tree/master/manuals/tube%20lens)  
Supplementary material on [piezoconcept](https://piezoconcept-store.squarespace.com/1-axis/p/fochs), and [technical drawings](https://github.com/venkatachalamlab/large-files/tree/master/drawings/assembly_piezo)  
