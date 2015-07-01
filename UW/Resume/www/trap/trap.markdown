
### Quantum Information with Trapped Ions

A quantum computer requires a quantum physical system that can be isolated from its environment long enough to perform computation. Interaction with uncontrolled environmental variables leads to decoherence and the loss of the quantum information stored in the system.  To perform the computation itself though the system must intereact with external control systems and have interactions between its components.  The goal, therefore, is to have a system that interacts strongly with well controlled computational systems, but that doesn't interact with very many other environmental variables.

Trapped ions are isolated from their environment inside an ultra high vacuum chamber, and have transitions that can store quantum information easily for seconds at the time.  External control with electric and magnetic fields is easily controlled, and ions are very sensitive to these controls.  Working with them requires an ion trap system and a lot of lasers.  I'll explain the basics of some of these systems in the next few sections.

### 3D Confinement

Basic electrostatics requires that in free space the electric potential $\phi$ obey

%{\large\[\nabla^2 \phi = 0\]}%

and therefore it is impossible to have $\partial_x^2 \phi > 0$, $\partial_y^2 \phi > 0$, and $\partial_z^2 \phi > 0$ at the same point in space which is the condition for having a stable trap in three dimensions.  The best possibility with electrostatics is to form a trap in 2 dimensions, but the thrid axis will always be an unstable equilibrium point.

Therefore to confine charged particle we have to use either magnetostatics or time-varying electric and magnetic fields.  Both of these possibilities are used in labs, but working with magnetostatics in so-called Penning traps requires that the ions precess about the magnetic field axis which makes performing quantum operations on them more difficult.  Instead, most quantum information efforts with trapped ions use Paul traps, which use radio frequency and dc electric fields to generate a stable trapping solution.


### <a name="paul_trap" /> Paul Traps

The easiest Paul trap geometry to understand features four long rods arranged in a square.  Radio frequency voltage is applied to two rods in opposite corners (red) and the other two rods are grounded (blue).  The rods provide radial confinement for the ions, and axial confinement is then provided by applying high voltage dc to two electrods centered inbetween the rods at opposite ends (purple).

<div class="figure center-image">
<img class="thumbnail" src="images/PaulTrap.png"/>
<p class="caption">The standard Paul trap geometry.</p>
</div>

At the center of the trap the rods form a radial oscillating quadrupole electric field that is a function of the frequency of the applied rf, $\Omega$.

%\large\[\Psi_{rf} = \kappa V_{rf} \cos( \Omega t ) \left( x^2 - y^2 \right) \]%

while the dc electrodes form a stable trap in the z (axial) direction, and an unstable equilibrium position in x and y.

%\large\[\Psi_{dc} = \kappa V_{dc} \left( z^2 - \frac{1}{2} \left( x^2 + y^2 \right) \right) \]%

The axial confinement is therefore straightforward and follows directly from just the dc potential.  The differential equation for the ions radial motion that arises from the rf potential is known as the Mathieu equation, and given certain requirements on the rf frequency and strength it forms a stable radial trapping potential.

<div class="figure center-image">
<img class="thumbnail" src="images/PaulTrap-ion_motion.png"/>
<p class="caption">Example ion radial motion in a Paul trap.</p>
</div>

A solution to the Mathieu equation given a starting location near the trap center is shown above.  The ion is confined radially with a restoring frequency corresponding to the slower oscillations seen above, while some faster oscillations that come directly from the applied rf frequency also perturb the ions' motion.  These fast oscillations are known as trap micromotion and are minimized as much as possible.

### Laser Cooling

Once the ions are confined they still usually have a lot of energy and random electric field perturbations tend to increase their temperature.  It's therefore necessary to continuously cool them using a technique called laser cooling.  Laser cooling requires a laser tuned near to a strong transition in the ion, and stable in frequency to some small fractions of the transition's linewidth.  With these requirements met, laser cooling is simply accomplished by tuning the laser to be slighty lower in frequency than the ions' resonance.

To understand how this achieves cooling one must consider the Doppler shift in the light frequency that the ion sees.  The Doppler shift (source frequency over observer frequency), as a function of the ions' velocity in the direction of the light $v$, is given by

%\large\[\frac{f_s}{f_o} = \sqrt{ \frac{1 + \frac{v}{c}}{1 - \frac{v}{c}} }\]%

The end result is that the ion will see the frequency of the laser as larger when the ion is moving towards the laser beam.  Therefore the ion absorbs more photons when it is moving towards the laser than when it is moving away.  These photons carry momentum in the direction of the laser and therefore absorbing them kicks the ions in the opposite direction of its motion and slows it down.  The ion immediately rescatters the photon, but does so in a random direction that averages to having little effect on its momentum.  Therefore, merely applying this laser to an ion decreases its temperature to a few millikelvin temperatures.  The light being reemitted by the ion from this laser can even be used to image the ion.

<div class="figure center-image">
<img class="thumbnail" src="images/BaYb.jpg"/>
<p class="caption">CCD image of flourescence from cooling Barium ions.</p>
</div>

The three panels above show two flourescing Barium ions in the same trap as a Ytterbium ion.  The Ytterbium ion has different transition frequencies than Barium and therefore does not flouresce when these lasers are applied.  Each bright area is a single ion.  The separation between them is approximately 7 microns, which is sufficient to focus laser beams well enough to largely interact with only one ion.

### Quantum Information

Once the ions are confined inside their trap and cooled by the cooling lasers, other lasers can be used to control different electronic states of the ions.  There are many accessible states in a trapped ion, and just by switching lasers quantum states be initialized and read out.

