#!/usr/local/bin/python2.7


from sys import exit, argv 
from os import environ, system
environ['KERAS_BACKEND'] = 'tensorflow'
environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np

from keras.models import Model, load_model 
from subtlenet import config 
from subtlenet.generators.gen_singletons import make_coll
from paths import basedir

model = load_model(argv[1])
name = argv[2]

system('rm -f %s/test/*_%s.npy'%(basedir,name))
coll = make_coll(basedir + '/PARTITION/*_CATEGORY.npy')

def predict_t(data):
    inputs = data['singletons'][:,[config.gen_singletons[x] for x in config.gen_default_variables]]
    if inputs.shape[0] > 0:
        mus = np.array(config.gen_default_mus)
        sigmas = np.array(config.gen_default_sigmas)
        inputs -= mus 
        inputs /= sigmas 
        r_shallow_t = model.predict(inputs)[:,config.n_truth-1]
    else:
        r_shallow_t = np.empty((0,1))

    return r_shallow_t 

coll.infer(['singletons'], f=predict_t, name=name, partition='test')
