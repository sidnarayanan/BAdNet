#!/usr/local/bin/python2.7

from sys import exit 
from os import environ, system
environ['KERAS_BACKEND'] = 'tensorflow'
environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
environ["CUDA_VISIBLE_DEVICES"] = ""


import numpy as np

from subtlenet import config, utils
from subtlenet.backend import obj 
from subtlenet.generators.gen import make_coll
basedir = environ['BASEDIR']
figsdir = environ['FIGSDIR']

n_batches = 500
partition = 'test'

p = utils.Plotter()
r = utils.Roccer()

OUTPUT = figsdir + '/' 
system('mkdir -p %s'%OUTPUT)

components = [
              'singletons',
              'shallow_nopt', 
#               'baseline_trunc4_limit50_best', 
#               'decorrelated_trunc4_limit50_best', 
#               'mse_decorrelated_trunc4_limit50_best', 
#               'emd_decorrelated_trunc4_limit50_best', 
              'baseline',
              'emd',
              'emd_clf_best',
              'mean_squared_error',
              'mean_squared_error_clf_best',
              'categorical_cross_entropy',
              'categorical_cross_entropy_clf_best',
              ]

colls = {
    't' : make_coll(basedir + '/PARTITION/Top_*_CATEGORY.npy',categories=components),
    'q' : make_coll(basedir + '/PARTITION/QCD_*_CATEGORY.npy',categories=components),
}


# run DNN
def predict(data,model):
    return data[model]

def access(data, v):
    return data['singletons'][:,config.gen_singletons[v]]

def div(data, num, den):
    return access(data, num) / np.clip(access(data, den), 0.0001, 999)

f_vars = {
    'nprongs' : (lambda x : access(x, 'nprongs'), np.arange(0,10,0.1), r'$N_\mathrm{prongs}$'),
    'tau32' : (lambda x : div(x, 'tau3', 'tau2'), np.arange(0,1.2,0.01), r'$\tau_{32}$'),
    'tau32sd' : (lambda x : div(x, 'tau3sd', 'tau2sd'), np.arange(0,1.2,0.01), r'$\tau_{32}^\mathrm{sd}$'),
    'partonm' : (lambda x : access(x, 'partonm'), np.arange(0,400,5), 'Parton mass [GeV]'),
    'msd'     : (lambda x : access(x, 'msd'), np.arange(0.,400.,20.), r'$m_\mathrm{SD}$ [GeV]'),
    'pt'        : (lambda x : access(x, 'pt'), np.arange(250.,1000.,50.), r'$p_\mathrm{T}$ [GeV]'),
    'shallow_nopt' : (lambda x : x['shallow_nopt'], np.arange(0,1.2,0.01), r'Shallow (no $p_{T}$) classifier'),
    'shallow_nopt_roc' : (lambda x : x['shallow_nopt'], np.arange(0,1.2,0.0001), r'Shallow (no $p_{T}$) classifier'),
    'baseline'  : (lambda x : x['baseline'], np.arange(0,1,0.01), 'Decorr (4,10)'),
    'baseline_roc'  : (lambda x : x['baseline'], np.arange(0,1,0.0001), 'Decorr (4,10)'),
    'emd'  : (lambda x : x['emd'], np.arange(0,1,0.01), 'Decorr (4,10)'),
    'emd_clf_best'  : (lambda x : x['emd_clf_best'], np.arange(0,1,0.01), 'Decorr (4,10)'),
    'emd_roc'  : (lambda x : x['emd'], np.arange(0,1,0.0001), 'Decorr (4,10)'),
    'emd_clf_best_roc'  : (lambda x : x['emd_clf_best'], np.arange(0,1,0.0001), 'Decorr (4,10)'),
    'mean_squared_error'  : (lambda x : x['mean_squared_error'], np.arange(0,1,0.01), 'Decorr (4,10)'),
    'mean_squared_error_clf_best'  : (lambda x : x['mean_squared_error_clf_best'], np.arange(0,1,0.01), 'Decorr (4,10)'),
    'mean_squared_error_roc'  : (lambda x : x['mean_squared_error'], np.arange(0,1,0.0001), 'Decorr (4,10)'),
    'mean_squared_error_clf_best_roc'  : (lambda x : x['mean_squared_error_clf_best'], np.arange(0,1,0.0001), 'Decorr (4,10)'),
    'categorical_cross_entropy'  : (lambda x : x['categorical_cross_entropy'], np.arange(0,1,0.01), 'Decorr (4,10)'),
    'categorical_cross_entropy_clf_best'  : (lambda x : x['categorical_cross_entropy_clf_best'], np.arange(0,1,0.01), 'Decorr (4,10)'),
    'categorical_cross_entropy_roc'  : (lambda x : x['categorical_cross_entropy'], np.arange(0,1,0.0001), 'Decorr (4,10)'),
    'categorical_cross_entropy_clf_best_roc'  : (lambda x : x['categorical_cross_entropy_clf_best'], np.arange(0,1,0.0001), 'Decorr (4,10)'),
}

roc_vars = {
            'tau32':(r'$\tau_{32}$',0,':'),
            'tau32sd':(r'$\tau_{32}^\mathrm{SD}$',2,':'),
            'shallow_nopt_roc':('Shallow',3,':'),
            'baseline_roc':('Baseline',4),
            'emd_roc':('EMD',7),
            'emd_clf_best_roc':('EMD best',7,'--'),
            'mean_squared_error_roc':('MSE',6),
            'mean_squared_error_clf_best_roc':('MSE best',6,'--'),
            'categorical_cross_entropy_roc':('CCE',5),
            'categorical_cross_entropy_clf_best_roc':('CCE best',5,'--'),
            }

order = [
        'tau32',
        'tau32sd',
        'shallow_nopt_roc',
        'baseline_roc',
        'emd_roc',
        'emd_clf_best_roc',
        'mean_squared_error_roc',
        'mean_squared_error_clf_best_roc',
        'categorical_cross_entropy_roc',
        'categorical_cross_entropy_clf_best_roc',
        ]

# unmasked first
hists = {}
for k,v in colls.iteritems():
    hists[k] = v.draw(components=components,
                      f_vars=f_vars,
                      n_batches=n_batches, partition=partition)

for k in hists['t']:
    if 'roc' in k:
        continue
    ht = hists['t'][k]
    hq = hists['q'][k]
    for h in [ht, hq]:
        h.scale()
    p.clear()
    p.add_hist(ht, '3-prong top', 'r')
    p.add_hist(hq, '1-prong QCD', 'k')
    p.plot(output=OUTPUT+k, xlabel=f_vars[k][2])

r.clear()
r.add_vars(hists['t'],           
           hists['q'],
           roc_vars,
           order
           )
r.plot(**{'output':OUTPUT+'roc'})


bkg_hists = {k:v for k,v in hists['q'].iteritems()}

# mask the top mass
def f_mask(data):
    mass = data['singletons'][:,config.gen_singletons['msd']]
    return (mass > 150) & (mass < 200)

hists = {}
for k,v in colls.iteritems():
    hists[k] = v.draw(components=components,
                      f_vars=f_vars,
                      n_batches=n_batches, partition=partition,
                      f_mask=f_mask)

for k in hists['t']:
    if 'roc' in k:
        continue
    ht = hists['t'][k]
    hq = hists['q'][k]
    for h in [ht, hq]:
        h.scale()
    p.clear()
    p.add_hist(ht, '3-prong top', 'r')
    p.add_hist(hq, '1-prong QCD', 'k')
    p.plot(output=OUTPUT+'mass_'+k, xlabel=f_vars[k][2])

r.clear()
r.add_vars(hists['t'],           
           hists['q'],
           roc_vars,
           order
           )
r.plot(**{'output':OUTPUT+'mass_roc'})



# get the cuts
thresholds = [0, 0.5, 0.75, 0.9, 0.99, 0.995]

def sculpting(name, f_pred):
    try:
        h = bkg_hists[name+'_roc']
    except KeyError:
        h = bkg_hists[name]
    tmp_hists = {t:{} for t in thresholds}
    f_vars2d = {
      'msd' : (lambda x : (x['singletons'][:,config.gen_singletons['msd']], f_pred(x)),
               np.arange(40,400,20.),
               np.arange(0,1,0.0001)),
      'pt' : (lambda x : (x['singletons'][:,config.gen_singletons['pt']], f_pred(x)),
               np.arange(400,1000,50.),
               np.arange(0,1,0.0001)),
      'partonm' : (lambda x : (x['singletons'][:,config.gen_singletons['partonm']], f_pred(x)),
               np.arange(0,400,20.),
               np.arange(0,1,0.0001)),
      }

    h2d = colls['q'].draw(components=components,
                          f_vars={}, f_vars2d=f_vars2d,
                          n_batches=n_batches, partition=partition)

    for t in thresholds:
        cut = 0
        for ib in xrange(h.bins.shape[0]):
           frac = h.integral(lo=0, hi=ib) / h.integral()
           if frac >= t:
               cut = h.bins[ib]
               break
    
        print 'For classifier=%s, threshold=%.3f reached at cut=%.3f'%(name, t, cut )
    
        for k,h2 in h2d.iteritems():
            tmp_hists[t][k] = h2.project_onto_x(min_cut=cut)

    
    colors = utils.default_colors
    for k in tmp_hists[thresholds[0]]:
        p.clear()
        p.ymin = 0.1
        p.ymax = 1e5
        for i,t in enumerate(thresholds):
            p.add_hist(tmp_hists[t][k], r'$\epsilon_\mathrm{bkg}=%.3f$'%(1-t), colors[i])
        p.plot(output=OUTPUT+'prog_'+name+'_'+k, xlabel=f_vars[k][2], logy=True)
        p.clear()
        for i,t in enumerate(thresholds):
            tmp_hists[t][k].scale()
            p.add_hist(tmp_hists[t][k], r'$\epsilon_\mathrm{bkg}=%.3f$'%(1-t), colors[i])
        p.plot(output=OUTPUT+'prognorm_'+name+'_'+k, xlabel=f_vars[k][2], logy=False)

sculpting('emd', f_pred = f_vars['emd'][0])
sculpting('emd_clf_best', f_pred = f_vars['emd_clf_best'][0])
sculpting('mean_squared_error', f_pred = f_vars['mean_squared_error'][0])
sculpting('mean_squared_error_clf_best', f_pred = f_vars['mean_squared_error_clf_best'][0])
sculpting('categorical_cross_entropy', f_pred = f_vars['categorical_cross_entropy'][0])
sculpting('categorical_cross_entropy_clf_best', f_pred = f_vars['categorical_cross_entropy_clf_best'][0])
sculpting('tau32sd', f_pred = f_vars['tau32sd'][0]) 
sculpting('baseline', f_pred = f_vars['baseline'][0])
sculpting('shallow_nopt', f_pred = f_vars['shallow_nopt'][0])

