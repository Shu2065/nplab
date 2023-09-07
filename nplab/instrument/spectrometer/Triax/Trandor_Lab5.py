"""
jpg66
"""
from __future__ import division
from __future__ import print_function

from builtins import input
from builtins import str
from past.utils import old_div
from nplab.instrument.spectrometer.Triax import Triax
import numpy as np
from nplab.instrument.camera.Andor import Andor, AndorUI
import types
import future
import h5py

Calibration_Arrays=[]

Calibration_Arrays.append([])
Calibration_Arrays.append([])
Calibration_Arrays.append([])

#Calibration_Arrays[0].append([546.,614.,633.,708.19,785.,880.])
#Calibration_Arrays[0].append([-1.54766997e-05, 3.12560316e-06, 7.48822074e-06, 1.26048704e-05 , 4.21666043e-06, 2.43945244e-05])
#Calibration_Arrays[0].append([-1.63503325e+00, -1.94141892e+00, -2.02516092e+00, -2.17431238e+00, -1.87265593e+00, -2.60909451e+00])
#Calibration_Arrays[0].append([1.44780946e+04, 1.75785703e+04, 1.85922568e+04, 2.17816013e+04, 1.10551705e+04, 3.03183653e+04])

Calibration_Arrays[1].append([540.05615, 614.3063, 633.44275, 703.2413, 794.31805, 885.3867])
Calibration_Arrays[1].append([7.119416e-06, 1.7002e-06, 1.7011041e-06, 1.5920945e-06, -4.0903983e-06, 1.2277135e-05])
Calibration_Arrays[1].append([-1.8436913, -1.8155332, -1.8185873, -1.8278793, -1.7779323, -1.983125])
Calibration_Arrays[1].append([7027.7876, 7947.521, 8205.945, 9151.439, 10238.555, 12075.545])


# Calibration_Arrays[2].append([540.056, 614.306, 633.443, 703.241, 837.761, 865.438])
# Calibration_Arrays[2].append([7.02044e-06, 6.48843e-06, 8.10113e-06, 8.42173e-06, 8.37878e-06, -2.02813e-05])
# Calibration_Arrays[2].append([-1.74032, -1.74138, -1.7393, -1.73926, -1.7405, -1.81753])
# Calibration_Arrays[2].append([1869.23, 2097.25, 2155.35, 2369.81, 2784.87, 2917.82])


#--by bd355
Calibration_Arrays[2].append([540.056, 614.306, 633.443, 703.241, 837.761, 865.438])
Calibration_Arrays[2].append([-6.9253952e-06, -6.4761766e-06, -7.1854643e-06, -8.4217318e-06, -7.6149108e-06, -7.3302917e-06])
Calibration_Arrays[2].append([-1.7404145, -1.7414042, -1.7393, -1.7392614, -1.7421813, -1.7428424])
Calibration_Arrays[2].append([1869.2498, 2097.2549, 2155.7705, 2369.8137, 2785.7876, 2822.447])
#--


#Calibration_Arrays[2].append(list(h5py.File("Calibration_Grating_2.h5", 'r')["Calibration_List"][0]))
#Calibration_Arrays[2].append(list(h5py.File("Calibration_Grating_2.h5", 'r')["Calibration_List"][1]))
#Calibration_Arrays[2].append(list(h5py.File("Calibration_Grating_2.h5", 'r')["Calibration_List"][2]))
#Calibration_Arrays[2].append(list(h5py.File("Calibration_Grating_2.h5", 'r')["Calibration_List"][3]))

Calibration_Arrays=np.array(Calibration_Arrays, dtype=object)

CCD_Size=1600 #Size of ccd in pixels

#Make a deepcopy of the andor capture function, to add a white light shutter close command to if required later
# Andor_Capture_Function=types.FunctionType(Andor.capture.__code__, Andor.capture.__globals__, 'Unimportant_Name',Andor.capture.__defaults__, Andor.capture.__closure__)

class Trandor(Andor):#Andor
    ''' Wrapper class for the Triax and the andor
    ''' 
    def __init__(self, white_shutter=None, triax_address = 'GPIB0::1::INSTR', use_shifts = False, laser = '_633'):
        print ('Triax Information:')
        super(Trandor,self).__init__()
        self.triax = Triax(triax_address, Calibration_Arrays,CCD_Size) #Initialise triax
        self.white_shutter = white_shutter
        self.triax.ccd_size = CCD_Size
        self.use_shifts = use_shifts
        self.laser = laser
        # self.triax.Grating(1)
        
        print ('Current Grating:'+str(self.triax.Grating()))
        print ('Current Slit Width:'+str(self.triax.Slit())+'um')
        self.metadata_property_names += ('slit_width', 'wavelengths')
        
    def Grating(self, Set_To=None):
        return self.triax.Grating(Set_To)

    def Generate_Wavelength_Axis(self, use_shifts=None):

        if use_shifts is None:
            use_shifts = self.use_shifts
        if use_shifts:
            if self.laser == '_633': centre_wl = 632.8
            elif self.laser == '_785': centre_wl = 784.81
            wavelengths = np.array(self.triax.Get_Wavelength_Array()[::-1])
            return ( 1./(centre_wl*1e-9)- 1./(wavelengths*1e-9))/100    
        else:
            return self.triax.Get_Wavelength_Array()[::-1]
    x_axis = property(Generate_Wavelength_Axis)

    @property
    def wavelengths(self):
        return self.Generate_Wavelength_Axis(use_shifts=False)
    @property
    def slit_width(self):
        return self.triax.Slit()

    def Test_Notch_Alignment(self):
        	Accepted=False
        	while Accepted is False:
        		Input=input('WARNING! A slight misalignment of the narrow band notch filters could be catastrophic! Has the laser thoughput been tested? [Yes/No]')
        		if Input.upper() in ['Y','N','YES','NO']:
        			Accepted=True
        			if len(Input)>1:
        				Input=Input.upper()[0]
        	if Input.upper()=='Y':
        		print ('You are now free to capture spectra')
        		self.Notch_Filters_Tested=True
        	else:
        		print ('The next spectrum capture will be allowed for you to test this. Please LOWER the laser power and REDUCE the integration time.')
        		self.Notch_Filters_Tested=None
    def Set_Center_Wavelength(self, wavelength):
        ''' backwards compatability with lab codes that use trandor.Set_Center_Wavelength'''
        self.triax.Set_Center_Wavelength(wavelength)    


def Capture(_AndorUI):
    if _AndorUI.Andor.white_shutter is not None:
        isopen = _AndorUI.Andor.white_shutter.is_open()
        if isopen:
            _AndorUI.Andor.white_shutter.close_shutter()
        _AndorUI.Andor.raw_image(update_latest_frame = True)
        if isopen:
            _AndorUI.Andor.white_shutter.open_shutter()
    else:
        _AndorUI.Andor.raw_image(update_latest_frame = True)
setattr(AndorUI, 'Capture', Capture)
   

  
    

