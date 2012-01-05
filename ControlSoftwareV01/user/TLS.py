from numpy import pi,arange,concatenate
import numpy
#from sympy import I,N
from scipy.integrate import quad
from scipy.interpolate import UnivariateSpline
from scipy import infty,imag,real,tanh,cosh,sinh,sqrt,arctan,log,arctanh

from scipy.constants import hbar,k

from SampleConstants import fm,Qclamp,Eta


#####TLS parameters
B = 1.6e-19
rho = 2330.0

cson = 5800.0
A = (3.0/cson**5*B**2.0/2/pi/rho/hbar**4*8*k**3)**(-1)
Pbar = 1.8e45## what's that?

def taumini(e,T):
    return A/T**3/e**3*tanh(e)


splineQrelaxCalculatedForFreq = dict()
splinedfrelaxCalculatedForFreq = dict()
#splineCalculatedForFreq["dfrelax"] = -1

def __invQrelax__(T,f = fm):
    w = 2*pi*f
    f = lambda e:1/(cosh(e))**2*w*(-1)/w*2*imag(sqrt(-1-taumini(e,T)*w*1j)*arctan(1/sqrt(-1-(taumini(e,T)*w)*1j)))
    integ = real(quad(f,0,infty)[0])
    return Pbar*B**2/rho/cson**2*integ

###define a spline to approximate this function :
def recalculateSplineQrelax(f = fm):
    X = arange(0.5,2,0.08)
    X = concatenate((X,arange(2,7,1)))
    Y = [__invQrelax__(x,f) for x in X]
#    _invQrelaxSpline_ = UnivariateSpline(X,real(Y),k=5)
    splineQrelaxCalculatedForFreq[f] = UnivariateSpline(X,real(Y),k=5)


def invQrelax(T,f = fm):
    try:
        func = splineQrelaxCalculatedForFreq[f]
    except KeyError:
        recalculateSplineQrelax(f)
        func = splineQrelaxCalculatedForFreq[f]
    return func(T)

#    for w in arange(20e6,150e6,5e6):
 #       x.append(T)
  #      y.append(w)
   #     z.append(invQrelax(T,w))


def invQres(T):
    w = 2*pi*fm
    return pi*B**2*Pbar/rho/cson**2*tanh(hbar*w/2/k/T)

invQclamp = 1.0/Qclamp

def invQTLS(T,f = fm):
    return invQres(T)+invQrelax(T,f)

def invQ(T):
    """returns the inverseQ change of the toroid as a function of T and Omega taking into account clamping losses and TLS theory from Olivier"""
#    try:
#        res = numpy.zeros(len(T))
#    except TypeError:
    return invQres(T)+invQrelax(T)+invQclamp
#    for i,t in enumerate(T):
#        res[i] = invQres(t,w)+invQrelax(t,w)+invQclamp
#   return res


def __dfrelax__(T,f = fm):
    w = f*2*pi
    f = lambda e:(1.0/(cosh(e))**2)*2.0*(-1.0 + real(sqrt(1.0 - (taumini(e, T)*w)*1j)*arctanh(1.0/sqrt(1.0-(taumini(e,T)*w)*1j))))
    integ = real(quad(f,0,infty)[0])
    return -Pbar*B**2/rho/2/cson**2*integ

###define a spline to approximate this function :
#X = arange(0.5,10,0.1)
def recalculateSplinedfrelax(f = fm):
    X = arange(0.5,2,0.08)
    X = concatenate((X,arange(2,7,1)))
    Y = [__dfrelax__(x,f) for x in X]
    splinedfrelaxCalculatedForFreq[f] = UnivariateSpline(X,real(Y),k=5)

def dfrelax(T,f = fm):
    try:
        func = splinedfrelaxCalculatedForFreq[f]
    except KeyError:
        recalculateSplinedfrelax(f)
        func = splinedfrelaxCalculatedForFreq[f]
    return func(T)

def dfres(T):
    return Pbar*B**2/rho/2/cson**2*log(T/.1)


def df(T,f = fm):
    """returns the relative frequency shift (dnu/nu) as a function of T and omega thanks to TLS theory from Olivier"""
#    try:
#        res = numpy.zeros(len(T))
#    except TypeError:
    return dfres(T) + dfrelax(T,fm)
#    for i,t in enumerate(T):
#        res[i] = dfres(t,w) + dfrelax(t,w)
#    return res



### according to my calculation Eta*Kappa*tau_ex = 1
def deltaTresonant(delta_hz,kappa_hz,split_hz,ampl):
    """returns the temperature elevation due to the absorption of a splitted resonnance detuned of delta_hz"""
    Delta = delta_hz*2*pi
    gamma = split_hz*2*pi
    Kappa = kappa_hz*2*pi
    tau_ex = 1/(Eta*Kappa)
    a = 1.0/2*(1/(Kappa/2-00000000))
    #return float(N(abs((4*I*Delta - 2*Kappa)/(-4*Delta**2 + gamma**2 - 4*I*Delta*Kappa+ Kappa**2))))
    numer = ((4*Delta**2 + Kappa**2)*(16*Delta**4 - 8*Delta**2*(gamma**2 - Kappa**2) + (gamma**2 + Kappa**2)**2))
    denom = ((Kappa**2-4*Delta**2+gamma**2)**2 + (4*Delta*Kappa)**2)**2
    return 4*numer/denom
