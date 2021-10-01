import glob
import os
import numpy as np
from astroplan import Observer
from astropy.time import Time
import astropy.units as u
from astropy.utils.iers import conf
conf.auto_max_age = None

now = Time.now()

date = '2021-10-01'
lco = Observer.at_site("lco")
#mmt = Observer.at_site('mmt', pressure=0*u.bar)

##'technical':['60.A-9700']
projects = ['brahm','moyano','zakhozhay','vines']
ids = {'brahm':['0108.A-9003'],'zakhozhay':[''],'moyano':['0108.A-9008', '0106.A-9004'],'vines':['0108.A-9007', '0106.A-9003']}

nights = {'moyano':['2021-12-28','2021-12-29'],\
		  'zakhozhay':['2021-10-22','2021-10-23','2021-10-24','2021-10-25','2021-10-26','2021-10-27','2021-10-28','2021-10-29','2021-10-30',\
			      '2022-03-16','2022-03-17','2022-03-18','2022-03-19','2022-03-20','2022-03-21','2022-03-22','2022-03-23'],\
		  'brahm':['2021-10-11','2021-10-12','2021-10-13','2021-10-14','2021-10-15','2021-10-16','2021-10-17','2021-10-18','2021-10-19','2021-10-20','2021-10-21',\
			  '2022-01-11','2022-01-12','2022-01-13','2022-01-14','2022-01-15','2022-01-16','2022-01-17','2022-01-18','2022-01-19','2022-01-20',\
			  '2022-03-04','2022-03-05','2022-03-06','2022-03-07','2022-03-08','2022-03-09','2022-03-10','2022-03-11','2022-03-12','2022-03-13','2022-03-14','2022-03-15'],\
		  'vines':['2021-10-05','2021-10-06','2021-10-07','2021-10-08','2021-12-24','2021-12-25','2021-12-26']
		  }
used = {'chaname':0,'brahm':0,'zakhozhay':0,'moyano':0,'vines':0}
full = {'chaname':0,'brahm':0,'zakhozhay':0,'moyano':0,'vines':0}
ratios=[]
available = 0.
date = Time(date+' 19:00')
while date < Time('2021-04-01 19:00'):

	tw1 = lco.twilight_evening_nautical(date, which='previous')
	tw2 = lco.twilight_morning_nautical(date, which='previous')
	ndur = float(str((tw2-tw1)*24.))


	for proj in projects:
		if str(date).split()[0] in nights[proj]:
			full[proj] += ndur
			if date > now:
				available += ndur 


	fil = 'nights/'+str(date).split()[0].replace('-','')+'.txt'
	if os.access(fil,os.F_OK):
		fle = open(fil,'r')
		flines = fle.readlines()
	else:
		flines = []
	tottime = 0
	for line in flines:
		cos = line.split()
		runID = cos[3]
		texp = cos[14]
		for proj in projects:
			pids = ids[proj]
			for pid in pids:
				if pid in runID:
					used[proj] += (float(texp)+240.)/3600.
					tottime += (float(texp) + 240.)/3600.
		#print(runID, texp)
		
	if len(flines)>0:
		ratios.append(tottime/ndur)

	##print(ndur,tottime/3600.)

	date += 1
ratios = np.array(ratios)

print('median efficiency ratio per night:',np.median(ratios))

print('used time per project:',used)

totfull= 0.
for proj in projects:
	full[proj] *= np.median(ratios)
	totfull += full[proj] 
available *= np.median(ratios)

props = {}
for proj in projects:
	props[proj] = full[proj]/totfull

print('Total time in semester per project:',full)
totused = 0
for proj in projects:
	totused+=used[proj]
print('total used time =', totused)
print('total available time =', available)
print('proportions =', props)

print('projected time left:')
for proj in projects:
	print(proj,props[proj]*(totused+available) - used[proj])


lines = ['# feros-pool\n', 'Computes used and available time for different observing projects\n','\n']
lines.append('projected time left computed on '+str(now)+':\n\n')

for proj in projects:
	lines.append('    '+proj+': '+str(props[proj]*(totused+available) - used[proj])+' h \n\n')

ff = open('README.md','w')
for line in lines:
	ff.write(line)
ff.close()




