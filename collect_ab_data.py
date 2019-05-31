"""
Store a model's results, where the model is implemented using the Allen Brain SDK
"""

# running an SDK model based on example at:
# https://github.com/AllenInstitute/AllenSDK/blob/gh-pages/_downloads/Pulse%20Stimulus.ipynb

import os
import sys
import numpy
import json

# switch to the directory containing the script
# solution modified from http://stackoverflow.com/questions/1432924/python-change-the-scripts-working-directory-to-the-scripts-own-directory
dirname = os.path.dirname(sys.argv[0])
if dirname:
    os.chdir(dirname)

os.system('nrnivmodl modfiles')

from allensdk.model.biophys_sim.config import Config
from allensdk.model.biophysical_perisomatic.utils import Utils
from allensdk.core.dat_utilities import DatUtilities


description = Config().load('manifest.json')
utils = Utils(description)
h = utils.h

# configure model
manifest = description.manifest
morphology_path = description.manifest.get_path('MORPHOLOGY')
utils.generate_morphology(morphology_path.encode('ascii', 'ignore'))
utils.load_cell_parameters()

# configure a simple current-clamp stimulus to generate some spikes
ic = h.IClamp(0.5, sec=h.soma[0])
ic.delay = 200
ic.dur = 1000

junction_potential = description.data['fitting'][0]['junction_potential']

currents = [270, 170, 110]
data = {'currents': currents, 'L': sum(sec.L for sec in h.allsec())}
h.tstop = 1500

for current in currents:
    ic.amp = current / 1000.
    vec = utils.record_values()
    h.dt = 0.00625
    h.run()
    data[current] = [[t / 1000., v - junction_potential] for t, v in zip(vec['t'], vec['v'])]

with open('../../temp_results_sdk.json', 'w') as f:
    f.write(json.dumps(data))


