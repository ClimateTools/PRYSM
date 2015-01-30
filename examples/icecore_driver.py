# Sylvia Dee 
# PSM d18O Ice Cores
# ENVIRONMENT SUB-MODEL
# a.k.a. driver script
# Modified 01/27/2015 <sdee@usc.edu>

"""
    Ice Core d18O Environment Model (Wrapper Script)
    ~ Load Environmental Variables to compute d18O calcite/dripwater.

    INPUTS:
        Isotope-Enabled GCM INPUTS:
        T       (Temperature, K)
        P       (Pressure, Atm)
        d18O    (Precipitation, permil) 

    Wrapper script runs the following submodels:

    icecore_sensor  (weighted d18O precip, altitude and temperature bias corrections)
    icecore_archive (diffusion, compaction)
    icecore_bam     (time uncertainties, analytical uncertainties)

    OUTPUTS: 
        d18O Ice Core Timeseries
"""
#======================================================================
# E0. Initialization
#======================================================================
from pydap.client import open_url  
from pylab import *
import numpy as np
import matplotlib.pyplot as plt

#======================================================================
# E1. Load input data/all environmental variables (annual averages)
#======================================================================

# LOAD TESTER FILES (OPTIONAL) or input your own data here.

# Near-Surface Air Temp [K]
T=np.load('temperature.npy')

# Accumulation Rate [m]
accum=np.load('accumulation.npy')

# Core Depth
depth=np.load('total_icecore_depth.npy')

# Depth horizons (accumulation per year corresponding to depth moving down-core)
depth_horizons=np.load('depth_horizons.npy')

#delta-18-O of precipitation (weighted) [permil]
d18Op=np.load('d18O_P.npy')

# Mean Surface Pressure [Atm]
P=1.0

# Set Time Axis
time=np.arange(1000,2005,1)

#======================================================================
# E2. Calculate Precip-Weighted Delta Values at one location
#======================================================================

deltaP = d18Op#your precip isotope data would go here

# reshape data sets: singular vector
# example: deltaP=deltaP.reshape(1005)

#======================================================================
# E3. CALL SENSOR MODEL
#======================================================================

# 4. Apply icecore_sensor to extract precipitation-weighted d18o record for each core
#    and compute altitude, temperature corrections. (Please see docstring icecore_sensor).

d18O     = deltaP# your dataset loaded here
alt_diff = 0.0      # alt_diff at location (m)
d18Oice  = icecore_sensor(time,d18O,alt_diff)

# returns: icecore

#======================================================================
# E4. CALL ARCHIVE MODEL
#======================================================================

# This archive model will calculate diffusion and compaction 
# (Please see docstrings: diffusivity, icecore_diffuse)
 
# NOTE: tester file has accumulation in meters per year. Below is optional unit conversion.

#accum=accum*365.0       # multiple by 365 days to get yearly accumulation in mm
#b = accum/1000.         # convert mm/yr to m/yr, accumulation rate (e.g. 1.3 m/year)

core_length=np.cumsum(b)
depth = core_length[-1]
depth_horizons=np.diff(core_length)#enter depth horizons downcore

# Set inputs for Archive Model

# For the Density Profile, we use average T, b
T=np.mean(T)
b=np.mean(b)

# Optional: set manually
#P = 1.# pressure in atmospheres
#T = 296.02# temperature (K), default value = 260 K

dz = min(depth_horizons)/10.#or 0.06# stepping in depth (m)
drho = 0.5# step in density (kg/m^3)
depth= depth# enter your ice core total depth/length in meters

z, sigma, D, time_d, diffs, ice_diffused = icecore_diffuse(d18Oice,b,time,T,P,depth,depth_horizons, dz,drho)

#======================================================================
# E5. CALL OBSERVATION MODEL
#======================================================================

# 5.1 Specify and model rate of annual layer miscount

X = ice_diffused
tp, Xp, tmc=bam_simul_perturb(X,t,param=[0.01,0.01],name='poisson',ns=1000,resize=0)
#======================================================================

# 5.2: Analytical Uncertainty Model:

#5.2.1 Simple Model: just add uncertainty bands based on measurement precision
sigma=0.1 # permil, measurement  precision
ice_upper, ice_lower = analytical_err_simple(X,sigma)

#5.2.2 Gaussian Noise Model for analytical error: 
sigma=0.1
nsamples = ## enter number of samples here
ice_Xn=analytical_error(X,sigma)
#======================================================================
# PLOTTING EXAMPLES 
#======================================================================

# Example 1: Diffusion Profiles

diffs =((np.diff(z)/np.diff(time_d)))
diffs=diffs[0:-1] 
# row and column sharing
f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
ax1.plot(z[0:-1],D*1e4)
ax2.plot(z[0:-2],sigma*100.0,color='c')
ax3.plot(z,time_d,color='r')
ax4.plot(z[0:-2],sigma/diffs,color='g')
# Set common labels
ax1.set_ylabel('diffusivity (cm^2/s)')
ax1.set_xlabel('Depth(m)')
ax2.set_ylabel('Diffusion length (cm)')
ax2.set_xlabel('Depth(m)')
ax3.set_ylabel('Age (yrs)')
ax3.set_xlabel('Depth (m)')
ax4.set_ylabel('Diffusion Length/Annual Layer Thickness')
ax4.set_xlabel('Depth (m)')
plt.suptitle('VOSTOK Diffusion Lengths')
plt.show()

#======================================================================

# Example 2: Plot age realizations with depth (THIS IS THE SAVED XP)

bam=Xp
bam.shape

depths=depth_horizons
depths=np.flipud(depths[:,0])

quel=ice_diffused

for i in range(len(bam[1])):
    plt.plot(bam[:,i],depths,color='0.75')
    
plt.rcParams['text.usetex']=True
plt.rcParams['text.latex.unicode']=True
plt.rcParams['font.family']='serif'

plt.plot(quel,depths,color='Blue')
#plt.legend(loc=3,fontsize=14,frameon=False)
#plt.xlim([1000,2010])
#plt.ylim([-25,-10])
plt.ylabel('Depth in Ice Core (m)')
plt.xlabel('Modeled $\delta^{18}O_{ICE}$')
plt.gca().invert_yaxis()
plt.title(r'\texttt{BAM} Simulated Chronologies, 2$\%$ error, Quelccaya Ice Cap, Peru')
plt.show()