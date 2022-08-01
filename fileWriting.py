import casperfpga
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import argparse
import time


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="fpg file to upload to red-pitaya")
parser.add_argument("-r", "--redpitaya", help="Red-Pitaya hostname or  IP address")
parser.add_argument("-a", "--accums", help="Number of accumulations",default=4)
parser.add_argument("-t", "--trials", help ="Number of Trials(bins) per spectra",default = 50) 
parser.add_argument("-n", "--spectra", help ="Number of Spectra per file",default = 1)
args = parser.parse_args()


red_pitaya = args.redpitaya
print("Connecting to Red Pitaya: {0}".format(red_pitaya))
fpga=casperfpga.CasperFpga(red_pitaya)

file_fpg=args.file
print("Uploading: {0}".format(file_fpg))
fpga.upload_to_ram_and_program(file_fpg)

fft_len=256
acc_len=int(args.accums)
trials = int(args.trials) 
spectra = int(args.spectra) 
snap_cyc=10

print("These are the devices in your design ...")
print(fpga.listdev())

fpga.write_int('acc_len',acc_len)
fpga.write_int('snap_gap',snap_cyc)
fpga.write_int('reg_cntrl',1)

time.sleep(5)


#preallocate space
fig0, ax0= plt.subplots()
fig1, ax1= plt.subplots()
fig2, ax2= plt.subplots()

w, h = fft_len, trials

empty_spectra_file_time = [[0 for x in range(w)]  for y in range(h)]

empty_spectra_file_pwr_fftshifted_256 = [[0 for x in range(w)]  for y in range(h)]
empty_spectra_file_frq_256 = [[0 for x in range(w)]  for y in range(h)]
empty_spectra_file_pwr_256 = [[0 for x in range(w)]  for y in range(h)]



frequency_shifted = [[0 for x in range(w)]  for y in range(h)]

for i in range(h):

	fpga.snapshots.accum0_snap_ss.arm()
	spec0=fpga.snapshots.accum0_snap_ss.read(arm=False)['data']

	fpga.snapshots.accumdat_snap_ss.arm()
	spec_dat=fpga.snapshots.accumdat_snap_ss.read(arm=False)['data']

	#declaring Variables
	spectrum0 = np.array(spec0['P_acc0'][0:2*acc_len*fft_len])	
        spectrum0_256 = spectrum0[:256]	

	
	freqs_MHz_256 = np.linspace(-256/2,256/2-1,256)*125/256	
	freqs_MHz_256_shift = np.fft.fftshift(freqs_MHz_256) #takes care of aliasing frequencies?

	
	#saving data
	empty_spectra_file_pwr_256[i] = spectrum0_256

	empty_spectra_file_pwr_fftshifted_256[i] = np.fft.fftshift(spectrum0_256[:256])

	empty_spectra_file_frq_256[i] = freqs_MHz_256
	frequency_shifted[i] = freqs_MHz_256_shift
	empty_spectra_file_time[i] = time.time()
	

	#ploting
	axis_x = range(w)
	y = spectrum0_256
	ax0.plot(axis_x, y)
	ax0.set(xlabel='bin',ylabel='power')

	#Plotting Power versus Channel
	ax1.plot(spec0['P_acc0'][0:2*acc_len*w],'b-')
	ax1.set(xlabel='channel',ylabel='power',title='Ch0')
	ax1.set_xlim(0,2*acc_len*w)

	#Plotting Power versus Frequency 
	spectrum0 = np.fft.fftshift(spectrum0_256)
	valid = np.array(spec0['val_acc0'][0:2*acc_len*w]).astype(bool)
	ax2.plot(freqs_MHz_256,spectrum0.astype(float),'b-') 
	ax2.set(xlabel='freq (MHz)',ylabel='power')
	ax2.set_xlim(0,50)
	
		
ax0.figure.savefig('Exp_Power_Point')
ax1.figure.savefig('Exp_Power_Channel')
ax2.figure.savefig('Exp_Power_Frequency')


#printing testing
try_y = np.array(empty_spectra_file_pwr_256)
try_y = try_y[:50,0:127]
try_x = freqs_MHz_256_shift[0:127]
#print(empty_spectra_file_pwr_128[20])
#print(freqs_MHz_128)
#print(freqs_MHz_128.shape)


#WaterFall
plt.figure()
img = plt.pcolormesh(try_x,list(range(50)),try_y)
plt.colorbar(img, ticks = [0])
plt.savefig('waterfall of pcolor')



#File Saving
filename = "spectra"
np.savez(filename,empty_spectra_file_pwr_256)

filename = "freq"
np.savez(filename,empty_spectra_file_frq_256)





#test plots
#ax3.figure.savefig('Spec0 Data Test PLot')
#ax4.figure.savefig('Freqs Data Test PLot')
#ax5.figure.savefig('Spec0_FFT Shifted Data Test PLot')



#Water Plots
#plt.figure()
#img = plt.pcolormesh(freqs_MHz,list(range(50)),empty_spectra_file_pwr_fftshifted)
#plt.colorbar(img, ticks = [0])
#plt.savefig('waterfall of pcolor')


#fig3, ax3= plt.subplots()
#fig4, ax4= plt.subplots() 
#fig5, ax5= plt.subplots() 
#fig6, ax6= plt.subplots() 




















