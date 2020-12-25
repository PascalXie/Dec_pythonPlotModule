import math
import numpy as np
import matplotlib.pyplot as plt

def ReadFile(path, fileName):
	print("Data File Path : {}".format(path))
	print("File Name : {}".format(fileName))

	# read
	f = open(path+fileName)
	lines = f.readlines()

	pos		= []
	normal	= []
	flag	= []

	for line in lines:
		line = line.strip().split()

		#alpha_cur = float(line[6]) #if alpha_cur==0:
		#	continue

		x		= float(line[0])
		y 	  	= float(line[1])
		z	  	= float(line[2])

		norx	= float(line[3])
		nory	= float(line[4])
		norz	= float(line[5])

		pos.append([x,y,z])
		normal.append([norx,nory,norz])
		flag.append(float(line[6]))

	pos = np.array(pos)
	normal = np.array(normal)

	return pos, normal

def EvaluateDistancesFromPointsToPlane(pos, norGT):
	#
	# Step 1 : GetPlaneParameters
	#
	# Plane function: Ax + By + Cz + D = 0
	# A = norx
	# B = nory
	# C = norz
	# D = -1./len(normals)*sum(Ax+By+Cz)

	A = norGT[0] 
	B = norGT[1]
	C = norGT[2]

	#print(A, B, C)

	# get D
	M_total = 0
	for i in range(len(pos)):
		p = pos[i]

		M_i = A*p[0] + B*p[1] + C*p[2]
		M_total += M_i
	
	D = M_total/float(len(pos))*(-1.)
	#print(D)

	#
	# Step 2 : GetPlaneParameters
	#
	dists = []
	for p in pos:
		x = p[0]
		y = p[1]
		z = p[2]
		dist = abs(A*x+B*y+C*z+D)#/math.sqrt(A**2+B**2+C**2)
		dists.append(dist)

	return dists;

def EvaluatePlaneSize(path, fileName, halfWidthOfCube):
	pos, normal = ReadFile(path, fileName)

	nCols = 640
	nRows = 480

	PlaneMarTop     = 100
	PlaneMarBottom  = 100
	PlaneMarLeft    = 100
	PlaneMarRight   = 100

	width = halfWidthOfCube*2

	distancesAllCubes = []
	for cubev in     range(int(PlaneMarTop/width), int((nRows-PlaneMarBottom)/width)):
		for cubeu in range(int(PlaneMarLeft/width),int((nCols-PlaneMarRight) /width)):
			cubeCentorv = cubev*width + 4
			cubeCentoru = cubeu*width + 4
			#print('cubeCentor v,u: ', cubeCentorv, cubeCentoru)

			cuveCentoridx = cubeCentorv*nCols + cubeCentoru
			norGT = normal[cuveCentoridx]
			if norGT[0]==0 and norGT[1]==0 and norGT[2]==-1:
				continue

			#print('cuveCentoridx: ',cuveCentoridx, 'norGT: ', norGT)

			posCur = []
			for v in range(int(cubeCentorv-width/2), int(cubeCentorv+width/2)):
				for u in range(int(cubeCentoru-width/2), int(cubeCentoru+width/2)):
					idx = v*nCols+u
					posCur.append(pos[idx])
					#print('idx: ',idx, 'pos[idx]: ',pos[idx])

			dists = EvaluateDistancesFromPointsToPlane(posCur, norGT)
			#print(dists)

			distancesAllCubes += dists
	
	distancesAllCubes = np.array(distancesAllCubes)
	DisMean		= np.mean(distancesAllCubes)
	DisStdDev	= np.std (distancesAllCubes)
	#print(DisMean, DisStdDev)

	return DisMean, DisStdDev

if __name__=='__main__':
	print('hello')

	# figure
	plt.figure(dpi=128,figsize=(6,5))

	fileName = 'data_NorMap_RGBCam_Control_350000.txt'
	
	Mean = []
	StdDev = [[],[]]
	WidthOfCube = []
	for halfWidthOfCube in range(5,30, 5):
		print('halfWidthOfCube: ',halfWidthOfCube)

		WidthOfCube.append(halfWidthOfCube*2)
		
		path = 'modelBack/'
		DisMean, DisStdDev = EvaluatePlaneSize(path, fileName, halfWidthOfCube)

		downStdDev = DisStdDev
		if DisMean-DisStdDev<0:
			downStdDev = DisMean 
		Mean.append(DisMean)
		StdDev[0].append(downStdDev)
		StdDev[1].append(DisStdDev)
	

	plt.errorbar(WidthOfCube, Mean, yerr=StdDev, marker='s', ms=6, capsize=2, elinewidth=2,  label='Back')


	Mean = []
	StdDev = [[],[]]
	WidthOfCube = []
	for halfWidthOfCube in range(5,30, 5):
		print(halfWidthOfCube)

		WidthOfCube.append(halfWidthOfCube*2)

		path = 'modelFront/'
		DisMean, DisStdDev = EvaluatePlaneSize(path, fileName, halfWidthOfCube)

		downStdDev = DisStdDev
		if DisMean-DisStdDev<0:
			downStdDev = DisMean 
		Mean.append(DisMean)
		StdDev[0].append(downStdDev)
		StdDev[1].append(DisStdDev)

	plt.errorbar(WidthOfCube, Mean, yerr=StdDev, marker='s', ms=6, capsize=2, elinewidth=1, label='Front')

	# set lable 
	plt.xlabel('Width of Cube / pixels',fontsize = 12)
	plt.ylabel('Distances / mm',	 fontsize = 12)

	# set limits
	#plt.xlim(-5000,110000) 
	#plt.ylim(0,20)

	# set title
	plt.title("Distances of Points to the Plane with Different Sizes",fontsize=12)

	# draw legend
	plt.legend()

	# tight layout
	plt.tight_layout()

	# save figure
	plt.savefig('figure_step20_evaluationOfPlaneSizes.png')

	# print figure on screen
	plt.show()

