import numpy as np, pylab as pl, cPickle
from linslens.ClipResult import clipburnin
from astLib import astCalc
import pyfits as py
from tools import solarmag

def VBI(name,bbands=True):
    lp, trace,det,_ = np.load('/data/ljo31b/EELs/inference/new/huge/result_212_CHECK_'+name)
    RE = re[name==names]

    for key in det.keys():
        det[key] = det[key][5000:,0].ravel()
    
    LOGIVV = det[key]*0.
    LOGIB,LOGIV = LOGIVV*0.,LOGIVV*0.

    for n in range(det[key].size):
        L = np.array([det[key][n] for key in ['logtau_V lens', 'tau lens', 'age lens','logZ lens']])
        S = np.array([det[key][n] for key in ['logtau_V source', 'tau source', 'age source','logZ source']])
        M = [det[key][n] for key in ['massL', 'massS']]
        M = [det[key][n] for key in ['massL', 'massS']]
        doexp = [True,False,False,True]
        doexp = np.array(doexp)==True
        L[doexp] = 10**L[doexp]
        S[doexp] = 10**S[doexp]
        l = np.atleast_2d([L])
        s = np.atleast_2d([S])
        ml,ms = M

        # ultimately, do this
        V = model.models['V_Johnson'].eval(s) - 2.5*ms
        B = model.models['B_Johnson'].eval(s) - 2.5*ms
        I = model.models['I_Cousins'].eval(s) - 2.5*ms
        if bbands:
            v = model.models[bands[name]+'_ACS'].eval(s) - 2.5*ms
        else:
            #print 'assuming F606W all the time'
            v = model.models['F606W_ACS'].eval(s) - 2.5*ms

        Lv = 0.4*(Vsun-V)
        Lb = 0.4*(Bsun-B)
        #Li = 0.4*(Isun-I)
        Lvv = 0.4*(vsun-v)

        logIv = Lv - np.log10(2.*np.pi*RE**2.)
        logIb = Lb - np.log10(2.*np.pi*RE**2.)
        #logIi = Li - np.log10(2.*np.pi*RE**2.)
        logIvv = Lvv - np.log10(2.*np.pi*RE**2.)
        LOGIVV[n] = logIvv
        LOGIV[n] = logIv
        LOGIB[n] = logIb
    return LOGIVV, LOGIV, LOGIB



names = py.open('/data/ljo31/Lens/LensParams/Phot_1src_huge_new.fits')[1].data['name']
szs = np.load('/data/ljo31/Lens/LensParams/SourceRedshiftsUpdated.npy')[()]
bands = np.load('/data/ljo31/Lens/LensParams/HSTBands.npy')[()]

names = szs.keys()
names.sort()

phot = py.open('/data/ljo31/Lens/LensParams/Phot_2src_huge_new_new.fits')[1].data
names = phot['name']
re = phot['Re v']
array = np.zeros((names.size,6))

for name in names:
    filename = '/data/ljo31b/EELs/spsmodels/wide/BIV_F606W_z0_chabBC03.model'
    f = open(filename,'rb')
    model = cPickle.load(f)
    f.close()

    z = model.redshifts[0]
    Bsun, Vsun, Isun, vsun = solarmag.getmag('B_Johnson',z),solarmag.getmag('V_Johnson',z),solarmag.getmag('I_Cousins',z), solarmag.getmag(bands[name]+'_ACS',z) #7.1,5.8,4.4,5.33    #5.48, 4.83, 4.08, 4.72

    dl = astCalc.dl(z)
    if z == 0.:
        dl = 10.
    DM = 5*np.log10(dl*1e6)-5.
      
    #Bsun, Vsun, Isun, vsun = Bsun+DM, Vsun+DM, Isun+DM, vsun+DM
    
    VV,V,B = VBI(name,bbands=False)
    
    print VV, V, B
    Bmed,Bup,Blo = np.median(B), np.percentile(B,84),np.percentile(B,16)
    Vmed,Vup,Vlo = np.median(V), np.percentile(V,84),np.percentile(V,16)
    array[name==names] = [Bmed,Bup,Blo,Vmed,Vup,Vlo]

    np.save('/data/ljo31/Lens/LensParams/B_V_redshift0_model_marginalised',array)

'''
    
    array[name==names] = logIvv

np.save('/data/ljo31/Lens/LensParams/F606W_rightredshifts_model',array)

Ahst = np.load('/data/ljo31/Lens/LensParams/Alambda_hst.npy')[()]
array2 = array*0.
mag = phot['mag v']
for ii in range(names.size):
    name = names[ii]
    array2[ii] =  solarmag.mag_to_logI(mag[ii]- Ahst[name][0],re[ii],bands[name]+'_ACS',szs[name][0])

np.save('/data/ljo31/Lens/LensParams/F606W_rightredshifts_data',array2)

# now do it at z=0
filename = '/data/ljo31b/EELs/spsmodels/wide/BIV_F606W_z0_chabBC03.model'
f = open(filename,'rb')
model = cPickle.load(f)
f.close()

z = model.redshifts[0]
Bsun, Vsun, Isun, vsun = solarmag.getmag('B_Johnson',z),solarmag.getmag('V_Johnson',z),solarmag.getmag('I_Cousins',z), solarmag.getmag('F606W_ACS',z) #7.1,5.8,4.4,5.33    #5.48, 4.83, 4.08, 4.72

phot = py.open('/data/ljo31/Lens/LensParams/Phot_2src_huge_new_new.fits')[1].data
names = phot['name']
re = phot['Re v']

array3 = array2*0.
array4 = array3*0.
for name in names:
    V,B,I,Lv,Lb,Li, logIv, logIb, logIi, v, Lvv, logIvv = VBI(name,bbands=False)
    #print name, '& $', '%.2f'%B, '$ & $', '%.2f'%V, '$ & $', '%.2f'%I, '$ &', '%.2f'%Lb, '&', '%.2f'%Lv, '&', '%.2f'%Li, '&', '%.2f'%logIb, '&', '%.2f'%logIv, '&', '%.2f'%logIi, '&', '%.2f'%v, '&', '%.2f'%Lvv, '&', '%.2f'%logIvv, r'\\'
    array3[name==names] = logIvv
    array4[name==names] = logIv
    print logIvv, logIv

np.save('/data/ljo31/Lens/LensParams/F606W_redshift0_model',array3)
np.save('/data/ljo31/Lens/LensParams/V_redshift0_model',array4)

'''
