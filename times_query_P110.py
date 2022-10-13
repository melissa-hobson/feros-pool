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
import matplotlib.pyplot as plt
plt.ion()
import datetime as dt

# to query archive directly
from astroquery.eso import Eso
eso = Eso()

# define runs and programs in run - only thing to change!
runs_compute = [2,3,4]
# programs is 3 or 4
programs_run = 4
# plot the runs or no
plots = False

# get time now
now = Time.now()

# set semester start date
date = '2022-10-01'

# set semester end date
semester_end = '2022-04-01 19:00'

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
ids = {'hobson':['0110.A-9011'],'zakhozhay':['0110.A-9013'],'moyano':['0110.A-9036'],'vines':['0110.A-9035']}

# list of nights assigned to each project
nights = {'moyano':['2023-01-07','2023-01-08','2023-01-09','2023-01-10'],\
		  'zakhozhay':['2022-10-25', '2022-10-26', '2022-10-27', '2022-10-28', '2022-10-29', '2022-10-30', \
                       '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24', '2023-01-25', '2023-01-26', '2023-01-27'],\
		  'hobson':['2022-10-15', '2022-10-16', '2022-10-17', '2022-10-18', '2022-10-19', \
                    '2022-11-08','2022-11-09','2022-11-10','2022-11-11','2022-11-12','2022-11-13','2022-11-14','2022-11-15','2022-11-16','2022-11-17','2022-11-18',\
                    '2022-12-13','2022-12-14','2022-12-15','2022-12-16','2022-12-17','2022-12-18',\
                    '2022-12-26','2022-12-27','2022-12-28','2022-12-29','2022-12-30','2022-12-31','2023-01-01','2023-01-02','2023-01-03',\
                    '2023-01-28','2023-01-29','2023-01-30','2023-01-31','2023-02-01','2023-02-02','2023-02-03','2023-02-04','2023-02-05','2023-02-06','2023-02-07'],\
		  'vines':['2022-10-04','2022-10-05','2022-10-06','2022-10-07','2022-10-08','2022-10-09',\
                   '2023-03-26','2023-03-27','2023-03-28','2023-03-29','2023-03-30','2023-03-31']
		  }


# list of all nights
all_nights = sorted({x for v in nights.values() for x in v})

# list of runs (consecutive nights grouped)
runs = {'run1':['2022-10-04','2022-10-05','2022-10-06','2022-10-07','2022-10-08','2022-10-09'],
        'run2':['2022-10-15', '2022-10-16', '2022-10-17', '2022-10-18', '2022-10-19'],
        'run3':['2022-10-25', '2022-10-26', '2022-10-27', '2022-10-28', '2022-10-29', '2022-10-30'],
        'run4':['2022-11-08','2022-11-09','2022-11-10','2022-11-11','2022-11-12','2022-11-13','2022-11-14','2022-11-15','2022-11-16','2022-11-17','2022-11-18'],
		'run5':['2022-12-13','2022-12-14','2022-12-15','2022-12-16','2022-12-17','2022-12-18'],
        'run6':['2022-12-26','2022-12-27','2022-12-28','2022-12-29','2022-12-30','2022-12-31','2023-01-01','2023-01-02','2023-01-03'],
        'run7':['2023-01-07','2023-01-08','2023-01-09','2023-01-10'],
        'run8':['2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24', '2023-01-25', '2023-01-26', '2023-01-27'],
        'run9':['2023-01-28','2023-01-29','2023-01-30','2023-01-31','2023-02-01','2023-02-02','2023-02-03','2023-02-04','2023-02-05','2023-02-06','2023-02-07'],
        'run10':['2023-03-26','2023-03-27','2023-03-28','2023-03-29','2023-03-30','2023-03-31']
		}

# gaps:
# 1-2: 5 nights
# 2-3: 5 nights
# 3-4: 8 nights
# 4-5: 24 nights
# 5-6: 7 nights
# 6-7: 3 nights
# 7-8: 10 nights
# 8-9: 0 nights (but 9 is shared with DDT)
# 9-10: 46 nights

# plot assigned & gap nights
if plots:
	hobson_dt = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in nights['hobson']]
	hobson_aux = np.ones(len(nights['hobson']))
	run9_dt = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in runs['run9']]
	run9_aux = np.ones(len(runs['run9']))
	zakhozhay_dt = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in nights['zakhozhay']]
	zakhozhay_aux = np.ones(len(nights['zakhozhay']))
	moyano_dt = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in nights['moyano']]
	moyano_aux = np.ones(len(nights['moyano']))
	vines_dt = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in nights['vines']]
	vines_aux = np.ones(len(nights['vines']))
	
	plt.figure()
	plt.scatter(hobson_dt, hobson_aux, label = 'Hobson')
	plt.scatter(zakhozhay_dt, zakhozhay_aux, label = 'Zakhozhay')
	plt.scatter(moyano_dt, moyano_aux, label = 'Moyano')
	plt.scatter(vines_dt, vines_aux, label = 'Vines')
	plt.scatter(run9_dt, run9_aux, label = 'DDT/Hobson')
	plt.legend()
	# run length labels
	for key in runs.keys():
		plt.text(dt.datetime.strptime(runs[key][0],'%Y-%m-%d').date()+dt.timedelta(len(runs[key])/3),0.995, str(len(runs[key]))+' n')
	# gaps labels
	plt.text(dt.datetime.strptime(runs['run1'][-1],'%Y-%m-%d').date()+dt.timedelta(2),1.01, '5 n')
	plt.text(dt.datetime.strptime(runs['run2'][-1],'%Y-%m-%d').date()+dt.timedelta(2),1.01, '5 n')
	plt.text(dt.datetime.strptime(runs['run3'][-1],'%Y-%m-%d').date()+dt.timedelta(4),1.01, '8 n')
	plt.text(dt.datetime.strptime(runs['run4'][-1],'%Y-%m-%d').date()+dt.timedelta(12),1.01, '24 n')
	plt.text(dt.datetime.strptime(runs['run5'][-1],'%Y-%m-%d').date()+dt.timedelta(3),1.01, '7 n')
	plt.text(dt.datetime.strptime(runs['run6'][-1],'%Y-%m-%d').date()+dt.timedelta(1),1.01, '3 n')
	plt.text(dt.datetime.strptime(runs['run7'][-1],'%Y-%m-%d').date()+dt.timedelta(5),1.01, '10 n')
	plt.text(dt.datetime.strptime(runs['run8'][-1],'%Y-%m-%d').date()+dt.timedelta(0),1.01, '0 n')
	plt.text(dt.datetime.strptime(runs['run9'][-1],'%Y-%m-%d').date()+dt.timedelta(23),1.01, '46 n')
	plt.xlabel('Date')

# list of assigned hours per project
# estimating from number of nights, taking 6.5h per night
assigned_nights = {'hobson':36.5,'zakhozhay':13,'moyano':4,'vines':12}
hours_night = 6.5
assigned = {}
for key in assigned_nights.keys():
	assigned[key] = assigned_nights[key]*hours_night

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
	print('median efficiency ratio per night could not be computed, assuming 0.75')
	med_effi = 0.75

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
# define initial proportions from full ("true" assigned) - used
proj_avail = {k: full[k] - used[k] for k in full}
total_avail = sum(proj_avail.values(), 0.0)
# initial proportions
props = {k: v / total_avail for k, v in proj_avail.items()}


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
	print(proj,round(full[proj] - used[proj],1))

# save to file
# create header line
lines = ['# feros-pool\n', 'Computes used and available time for different observing projects\n','\n']
# add line stating date of computation
lines.append('projected time left computed on '+now.to_value('iso', subfmt='date')+':\n\n')
# total time left per project
# loop over projects
for proj in projects:
	# add line with total time left
	lines.append('    '+proj+': '+str(round(props[proj]*(totused+available) - used[proj],1))+' h \n\n')

# loop over the requested runs
for run_i in runs_compute:
	run_key = 'run'+str(run_i)
	run_check = runs[run_key]
	nights_run = len(run_check)
	# print hours in run
	print('hours in '+run_key+' (nights = '+str(nights_run)+', '+str(run_check[0])+' - '+str(run_check[-1])+'):')
	# per project
	for proj in projects:
		# proportion * number of nights * 7.5h per night
		print(proj,round(props[proj]*nights_run*7.5,1))

	# save to file
	# time in this run per project
	lines.append('hours in '+run_key+' (nights = '+str(nights_run)+', '+str(run_check[0])+' - '+str(run_check[-1])+'):\n\n')
	# loop over projects
	for proj in projects:
		# add line with total time left
		lines.append('    '+proj+': '+str(round(props[proj]*nights_run*7.5,1))+' h \n\n')


# open file, write, close
ff = open('README.md','w')
for line in lines:
	ff.write(line)
ff.close()




