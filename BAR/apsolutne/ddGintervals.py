#!/usr/bin/env python3
# skripta za određivanje dG intervala funkcija koje ne rastu/padaju monotono

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from scipy import interpolate

plt.style.use('ggplot')

nsim = 6
x = np.linspace(0,1,100)
y = np.sin(12*x)-2*x

def find_intervals_old(x,y):
	""" Determines intervals of changing slope 
	and inflexion for a given function.	"""
	dy = np.gradient(y)
	ddy = np.diff(y,n=2)
	intervals = []
	prev_dy_sign,prev_ddy_sign = np.sign(0),np.sign(0)
	for idx1,item1 in enumerate(dy):
		current_x = x[idx1]
		current_dy_sign = np.sign(item1)
		if current_dy_sign != prev_dy_sign:
			intervals.append(current_x)
			prev_dy_sign = current_dy_sign
	# for idx2,item2 in enumerate(ddy):
	# 	current_x = x[idx1]
	# 	current_ddy_sign = np.sign(item2)
	# 	if current_ddy_sign != prev_ddy_sign:
	# 		intervals.append(current_x)
	# 	prev_ddy_sign = current_ddy_sign
	# intervals = np.unique(intervals)
	return intervals

#print(find_intervals(x,y))

# plt.plot(x,y,x,np.gradient(y))
# plt.show()
# plt.close
# plt.figure(2)
# plt.plot(np.linspace(0,10,len(ddy)),ddy)
# plt.show()
# plt.close()



def find_intervals(x,y):
    # input ddG_y_interp(ddG_x_interp)
    #x=np.linspace(0,20,num=500)  #  x = ddG_x_interp
    intervals = []
    dividedfunc = []
    start_i=0
    dy = np.gradient(y)
#    fig, ax = plt.subplots(figsize=(10, 8))
    k=0
    for i in range(len(dy)-1):
        #if dy[i]*dy[i+1] < 0:   zamijenjeno s ljepsim uvjetom
        if np.sign(dy[i]) != np.sign(dy[i+1]):
            k+=1
            print("motonic ddG(x) on interval [",x[start_i],x[i],"]")
            intervals.append([x[start_i],x[i]])
            dividedfunc.append([x[start_i:i],y[start_i:i]])
            #plt.subplot(320+k)
            plt.plot(x[start_i:i],y[start_i:i])
            start_i = i
    if k==0:
    	# If ddG is monotnous over the whole range return one interval
    	intervals.append([0.00,1.00])
    	dividedfunc.append([x,y])
    	plt.plot(x,y)
    # fix last interval
    if start_i != len(dy)-1:
        print("motonic ddG(x) on interval: [",x[start_i],x[-1],"]")
        intervals.append([x[start_i],x[-1]])
        dividedfunc.append([x[start_i:],y[start_i:]])
        plt.plot(x[start_i:],y[start_i:])
    return intervals,dividedfunc


def interval_weights(dividedfunc):
	""" Calculate how many lambdas should span each interval
	based on the maximal change in ddG. """
	weights = []
	for item in dividedfunc:
		ddGfunction_i = item[1]
		weights.append(np.abs(np.amax(ddGfunction_i)-np.amin(ddGfunction_i)))
	weights= weights/np.sum(weights)
	return weights

def lambdas_per_interval(nsim,weights):
	"""Assign proper number of lambdas per interval	based on calculated wieghts. """
	num_lambdas = []
	rounding_errors = []
	for item in weights:
		num_lambdas.append(int(np.floor(item*nsim)))
		rounding_errors.append(np.abs(item*nsim-np.floor(item*nsim)))
	sum_lambdas = np.sum(num_lambdas)
	if sum_lambdas<nsim:
		while True:
			print("Sum of weighted lambdas: ",sum_lambdas,"\n\tRounding errors: ",rounding_errors,"\n\tMax:",np.amax(rounding_errors),"Max_idx: ",np.argmax(rounding_errors))
			if sum_lambdas<nsim:
				if np.abs(sum_lambdas-nsim)>1 or num_lambdas[-1]!=0:
					max_idx = np.argmax(rounding_errors)
					num_lambdas[max_idx] += 1
					rounding_errors[max_idx] = 0
					sum_lambdas = np.sum(num_lambdas)
				elif num_lambdas[-1]==0 and np.abs(sum_lambdas-nsim)==1:
					print("Fixed last interval instead of weighted interval with corresponding maximum variance.")
					num_lambdas[-1] += 1
					sum_lambdas = np.sum(num_lambdas)
			else:
				break
	elif sum_lambdas>nsim:
		print("EROOR: Could not assign weighted number of lambdas per each interval. \n Nsim > N(weighted lambdas)")
		raise SystemExit(0) # prekida program
	return num_lambdas,sum_lambdas


if __name__ == '__main__':
	intervals,ddGfunction = find_intervals(x,y)
	weights = interval_weights(ddGfunction)
	print("Weights: ",weights)
	print(lambdas_per_interval(nsim,weights))

	plot_labels = ["[{:.2f}, {:.2f}]".format(k[0],k[1]) for k in intervals]
	plt.xlabel(r'$\lambda$') 
	plt.ylabel(r"$\Delta \Delta G / \mathrm{kJ mol^{-1}}$")
	plt.legend(plot_labels, loc='best')
#	plt.show()
	plt.savefig("ddG_intervals.pdf")
