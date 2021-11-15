# =============================================================================
# Imports and set up
# =============================================================================

import glob
import os
import numpy as np
from astroplan import Observer
from astropy.time import Time
import astropy.units as u
from astropy.utils.iers import conf
conf.auto_max_age = None

# to query archive directly
from astroquery.eso import Eso
eso = Eso()

# get time now
now = Time.now()

# set semester start date
date = '2021-10-20'

# set semester end date
semester_end = '2022-03-31 19:00'

# set up observing site (Las Camapanas)
# TODO can we get La Silla? Maybe using astropy? Does it matter
lco = Observer.at_site("lco")
#mmt = Observer.at_site('mmt', pressure=0*u.bar)

# =============================================================================
# define programs and nights
# =============================================================================

##'technical':['60.A-9700']
# list of projects
projects = ['brahm','moyano','zakhozhay','vines']
# list of IDs per project
ids = {'brahm':['0108.A-9003'],'zakhozhay':['0108.A-9029'],'moyano':['0108.A-9008', '0106.A-9004'],'vines':['0108.A-9007', '0106.A-9003']}
# list of nights assigned to each project
nights = {'moyano':['2021-12-28','2021-12-29','2021-12-30'],\
		  'zakhozhay':['2021-10-22','2021-10-23','2021-10-24','2021-10-25','2021-10-26','2021-10-27','2021-10-28','2021-10-29','2021-10-30',\
			      '2022-03-16','2022-03-17','2022-03-18','2022-03-19','2022-03-20','2022-03-21','2022-03-22','2022-03-23'],\
		  'brahm':['2021-10-11','2021-10-12','2021-10-13','2021-10-14','2021-10-15','2021-10-16','2021-10-17','2021-10-18','2021-10-19','2021-10-20','2021-10-21',\
			  '2022-01-11','2022-01-12','2022-01-13','2022-01-14','2022-01-15','2022-01-16','2022-01-17','2022-01-18','2022-01-19','2022-01-20',\
			  '2022-03-04','2022-03-05','2022-03-06','2022-03-07','2022-03-08','2022-03-09','2022-03-10','2022-03-11','2022-03-12','2022-03-13','2022-03-14','2022-03-15'],\
		  'vines':['2021-10-05','2021-10-06','2021-10-07','2021-10-08','2021-10-09','2021-12-24','2021-12-25','2021-12-26','2021-12-27']
		  }

# initialize used and full time per project
used = {'chaname':0,'brahm':0,'zakhozhay':0,'moyano':0,'vines':0}
full = {'chaname':0,'brahm':0,'zakhozhay':0,'moyano':0,'vines':0}
# initialize ratios
ratios=[]
# intiialize available time - one for all 
available = 0.

# =============================================================================
# Compute used and available time
# =============================================================================

# set start time to 7pm
date = Time(date+' 19:00')

# loop over dates until end of semester
while date < Time(semester_end):
	# get evening and morning twilight for date and location
	tw1 = lco.twilight_evening_nautical(date, which='previous')
	tw2 = lco.twilight_morning_nautical(date, which='previous')
	# compute time between twilights in hours
	ndur = float(str((tw2-tw1)*24.))

	# loop over projects
	for proj in projects:
		# if the date is in project nights
		if str(date).split()[0] in nights[proj]:
			# add night time to "full" count for the project
			full[proj] += ndur
			# if the date is in the future
			if date > now:
				# also add night time to "available" count (one for all)
				available += ndur 

	# check text files for the night
	# define file name
	fil = 'nights/'+str(date).split()[0].replace('-','')+'.txt'
	# if it exists open it
	if os.access(fil,os.F_OK):
		fle = open(fil,'r')
		flines = fle.readlines()
	# otherwise set to empty array
	else:
		flines = []
	# initialize night time count for all projects as 0
	tottime = 0
	# loop over the lines
	for line in flines:
		# get the run PID and exposure time for each spectrum
		cos = line.split()
		runID = cos[3]
		texp = cos[14]
		# loop over the projects
		for proj in projects:
			# get the PIDs
			pids = ids[proj]
			# loop over the PIDs
			for pid in pids:
				# if the pid matches the run PID
				if pid in runID:
					# add the exposure time (in h, plus 240s overhead) to project used time
					used[proj] += (float(texp)+240.)/3600.
					# add the time to the total time used for all projects
					tottime += (float(texp) + 240.)/3600.
		#print(runID, texp)
	# if the night file is not empty	
	if len(flines)>0:
		# append total time for all projects/night duration to ratios
		ratios.append(tottime/ndur)

	# increase date by 1
	date += 1

# convert ratios to array
ratios = np.array(ratios)

# =============================================================================
# Outputs
# =============================================================================

# print median efficiency per night
print('median efficiency ratio per night:',np.median(ratios))

# print used time per project
print('used time per project:',used)

# TODO why are we doing this?
# initialize total full count
totfull= 0.
# loop over projects
for proj in projects:
	# multiply full time per project by median efficiency
	full[proj] *= np.median(ratios)
	# add to total full count
	totfull += full[proj] 
# multiply available time for all projects by median efficiency
available *= np.median(ratios)

# initialize proportions
props = {}
# loop over projects
for proj in projects:
	# compute proportions as full (times ratios) over total full 
	# TODO are we not just re-removing the median efficiency??
	props[proj] = full[proj]/totfull

# print total used time, available time, proportions
print('Total time in semester per project:',full)
totused = 0
for proj in projects:
	totused+=used[proj]
print('total used time =', totused)
print('total available time =', available)
print('proportions =', props)

# print projected time left
print('projected time left:')
# per project
for proj in projects:
	# proportion for project times (total used+available) - used for project
	print(proj,props[proj]*(totused+available) - used[proj])
	# TODO WHY SO CONVOLUTED?

# save to file
# create header line
lines = ['# feros-pool\n', 'Computes used and available time for different observing projects\n','\n']
# add line stating date of computation
lines.append('projected time left computed on '+str(now)+':\n\n')

# loop over projects
for proj in projects:
	# add line with time left
	lines.append('    '+proj+': '+str(props[proj]*(totused+available) - used[proj])+' h \n\n')

# open file, write, close
ff = open('README.md','w')
for line in lines:
	ff.write(line)
ff.close()




