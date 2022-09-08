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

# define nights and programs in run - only thing to change!
nights_run = 10
# programs is 3 or 4
programs_run = 4

# get time now
now = Time.now()

# set semester start date
date = '2022-04-01'

# set semester end date
semester_end = '2022-09-30 19:00'

# set up observing site (Las Camapanas)
# TODO can we get La Silla? Maybe using astropy? Does it matter
lco = Observer.at_site("lco")
#mmt = Observer.at_site('mmt', pressure=0*u.bar)

# set eso query row limit - setting to -1 doesn't work properly!
eso.ROW_LIMIT = 100000

# =============================================================================
# define programs and nights
# =============================================================================

##'technical':['60.A-9700']

# list of projects
projects = ['hobson','zakhozhay','moyano','vines']

# list of IDs per project
ids = {'hobson':['109.A-9003'],'zakhozhay':['109.A-9014'],'moyano':['0109.A-9025'],'vines':['0109.A-9024']}

# list of nights assigned to each project
nights = {'moyano':['2022-07-27', '2022-07-28', '2022-07-29', '2022-09-11','2022-09-12','2022-09-13'],\
		  'zakhozhay':['2022-04-09', '2022-04-10', '2022-04-11', '2022-04-12', '2022-04-13', '2022-04-14', '2022-04-15', '2022-04-16', '2022-04-17', '2022-04-18', '2022-04-19', '2022-04-20', '2022-04-21'],\
		  'hobson':['2022-06-25', '2022-06-26', '2022-06-27', '2022-06-28', '2022-06-29', '2022-06-30', '2022-07-01', '2022-07-02', '2022-07-03', '2022-07-04', '2022-07-05', '2022-07-06', '2022-07-07', \
                    '2022-07-08', '2022-07-09', '2022-07-10', '2022-07-11', '2022-07-12', '2022-07-13', \
                    '2022-08-08', '2022-08-09', '2022-08-10', '2022-08-11', '2022-08-12', '2022-08-13', '2022-08-14', '2022-08-15', '2022-08-16', '2022-08-17', '2022-08-18', '2022-08-19', '2022-08-20', \
                    '2022-09-21','2022-09-22','2022-09-23','2022-09-24','2022-09-25','2022-09-26','2022-09-27','2022-09-28','2022-09-29','2022-09-30'],\
		  'vines':['2022-05-02', '2022-05-03', '2022-05-04', '2022-05-05', '2022-05-06']
		  }


# list of all nights
all_nights = sorted({x for v in nights.values() for x in v})

# list of runs (consecutive nights grouped)
runs = {'run1':['2022-04-09', '2022-04-10', '2022-04-11', '2022-04-12', '2022-04-13', '2022-04-14', '2022-04-15', '2022-04-16', '2022-04-17',
                '2022-04-18', '2022-04-19', '2022-04-20', '2022-04-21'],
        'run2':['2022-05-02', '2022-05-03', '2022-05-04', '2022-05-05', '2022-05-06'],
        'run3':['2022-06-25', '2022-06-26', '2022-06-27', '2022-06-28', '2022-06-29', '2022-06-30', '2022-07-01', '2022-07-02', '2022-07-03', 
                '2022-07-04', '2022-07-05', '2022-07-06', '2022-07-07', '2022-07-08', '2022-07-09', '2022-07-10', '2022-07-11', '2022-07-12', '2022-07-13'],
        'run3b':['2022-07-27', '2022-07-28', '2022-07-29'],
		'run4':['2022-08-08', '2022-08-09', '2022-08-10', '2022-08-11', '2022-08-12', '2022-08-13', '2022-08-14', '2022-08-15', '2022-08-16', '2022-08-17', 
                '2022-08-18', '2022-08-19', '2022-08-20'],
        'run5':['2022-09-11','2022-09-12','2022-09-13'],
        'run6':['2022-09-21','2022-09-22','2022-09-23','2022-09-24','2022-09-25','2022-09-26','2022-09-27','2022-09-28','2022-09-29','2022-09-30']
		}

# list of assigned hours per project
# estimating moyano & vines from number of nights
# notes: hobson + zhakozay have 52 nights for 216 hours, meaning 4.9h per night
# vines only has half the night on the last of that run
# moyano = 3*4.9 = 14.7 ~ 15 h
# vines = 4.5*4.9 = 22.09 ~ 22 h
#assigned = {'hobson':157,'zakhozhay':59,'moyano':15,'vines':22}
# September new runs:
# moyano: 3 more nights = 3*4.9 = 14.7 ~ 15 h
# hobson/zakhozhay 10 more nights: assume same 38-62 split
# hobson: 10*4.9*0.62 = 30.38 ~ 30 h
# zakhozhay: 10*4.9*0.38  = 18.62 ~ 19 h
assigned = {'hobson':187,'zakhozhay':78,'moyano':30,'vines':22}

# proportions from assigned hours
total_assi = sum(assigned.values(), 0.0)
prop_assi = {k: v / total_assi for k, v in assigned.items()}

# initialize used and full time per project
used = {'hobson':0,'zakhozhay':0,'moyano':0,'vines':0}
full = {'hobson':0,'zakhozhay':0,'moyano':0,'vines':0}
# initialize efficiency ratio (used time/total night time)
ratios=[]
# intiialize available time - one for all 
available = 0.
# initialize night durations
night_dur = []

# =============================================================================
# Compute used and available time
# =============================================================================

# loop over dates in all_nights list
for date in all_nights:
	# set start time to 7pm
	date = Time(date+' 19:00')
	# get evening and morning twilight for date and location
	tw1 = lco.twilight_evening_nautical(date, which='previous')
	tw2 = lco.twilight_morning_nautical(date, which='previous')
	# compute time between twilights in hours
	ndur = float(str((tw2-tw1)*24.))
	night_dur.append(ndur)

	# loop over projects
	for proj in projects:
		# if the date is in project nights
		if str(date).split()[0] in nights[proj]:
			# if the date is in the future
			if date > now:
				# also add night time to "available" count (one for all)
				available += ndur 

	# if the date is in the past:
	if date < now:
		# query eso archive for the night
		night = str(date).split()[0]
		data=eso.query_main(column_filters={'instrument':'FEROS','night':night},
		                columns=('OBJECT','RA','DEC','Program_ID','Instrument',
		                         'Category','Type','Mode','Dataset ID','Release_Date',
		                         'TPL ID','TPL START','Exptime','Exposure',
		                         'filter_lambda_min','filter_lambda_max','MJD-OBS',
		                         'Airmass','DIMM Seeing at Start'))#,'pi_coi'))

		# initialize night time count for all projects as 0
		tottime = 0

		# test loop for empty query results
		if data is not None:

			# loop over the projects
			for proj in projects:
				# get the PIDs
				pids = ids[proj]
				# loop over the PIDs
				for pid in pids:
					# find the entries with this pid
					aux_mask = np.char.find(data['Program_ID'],pid)
					mask = np.where(aux_mask!=-1)
					# check that mask is not empty
					if mask[0].size > 0:
						# add the exposure time (in h, plus 240s overhead) to project used time
						used[proj] += np.sum(data['Exptime'][mask]+240)/3600.
						# add the time to the total time used for all projects
						tottime += np.sum(data['Exptime'][mask]+240)/3600.
		else: 
			print('no data retrieved for night '+night)		
			data = np.array([])

		# if the night query is not empty	
		if len(data)>0:
			# append total time for all projects/night duration to ratios
			ratios.append(tottime/ndur)

# calculate full time from initial proportions and median night duration
# the 70% comes in later
for key in assigned.keys():
	full[key] = prop_assi[key]*np.median(np.array(night_dur))*len(all_nights)

# convert ratios to array
ratios = np.array(ratios)

# =============================================================================
# Outputs
# =============================================================================

# print median efficiency per night
if len(ratios)>0:
	print('median efficiency ratio per night:',np.median(ratios))
	med_effi = np.median(ratios)
else:
	print('median efficiency ratio per night could not be computed, assuming 0.7')
	med_effi = 0.7

# print used time per project
print('used time per project:',used)

# Incorporate median efficiency
# initialize total full count
totfull= 0.
# loop over projects
for proj in projects:
	# multiply full time per project by median efficiency
	full[proj] *= med_effi
	# add to total full count
	totfull += full[proj] 
# multiply available time for all projects by median efficiency
available *= med_effi

# get proportions
# note olga prefers to not have time on <week runs
# define initial proportions from full ("true" assigned) - used
proj_avail = {k: full[k] - used[k] for k in full}
total_avail = sum(proj_avail.values(), 0.0)
# initial proportions
prop_init = {k: v / total_avail for k, v in proj_avail.items()}
# make list
props_init = list(prop_init.values())
# compute proportions for redistributed time
# initialize proportions
props = {}
# check how many programs in run:
if programs_run == 4:
	# loop over projects
	for proj in projects:
		if proj == 'zakhozhay':
			props[proj] = prop_init[proj]+nights_run*prop_init[proj]/57
		else:
			props[proj] = prop_init[proj]-nights_run*prop_init['zakhozhay']/(3*57)
	# renormalize proportions
	props_sum = sum(props.values(), 0.0)
	props = {k: v / props_sum for k, v in props.items()}
elif programs_run == 3:
		for proj in projects:
			if proj == 'zakhozhay':
				props[proj] = 0
			else:
				props[proj] = prop_init[proj]+nights_run*prop_init['zakhozhay']/(3)
		# renormalize proportions
		props_sum = sum(props.values(), 0.0)
		props = {k: v / props_sum for k, v in props.items()}


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

# print total time left
print('total time left:')
# per project
for proj in projects:
	# total-used
	print(proj,full[proj] - used[proj])

# print hours in run
print('hours in run (nights = '+str(nights_run)+'):')
# per project
for proj in projects:
	# proportion * number of nights * 7.5h per night
	print(proj,props[proj]*nights_run*7.5)

# save to file
# create header line
lines = ['# feros-pool\n', 'Computes used and available time for different observing projects\n','\n']
# add line stating date of computation
lines.append('projected time left computed on '+str(now)+':\n\n')

# total time left per project
# loop over projects
for proj in projects:
	# add line with total time left
	lines.append('    '+proj+': '+str(props[proj]*(totused+available) - used[proj])+' h \n\n')

# time in this run per project
lines.append('hours in run (nights = '+str(nights_run)+'):\n\n')
# loop over projects
for proj in projects:
	# add line with total time left
	lines.append('    '+proj+': '+str(props[proj]*nights_run*7.5)+' h \n\n')


# open file, write, close
ff = open('README.md','w')
for line in lines:
	ff.write(line)
ff.close()




