#from scipy import tanh
#from sympy import *


from scipy.integrate import quad
#from scipy import *
#from sympy import I,abs,N
#from numpy import pi
from SampleConstants import *



def deltaGamma(delta_hz,kappa_hz = Kappa/(2*pi),split_hz = Gamma/(2*pi),sbar = sbar):
    """parameters should be in Hz!!!"""
    sbard = sbar
    Delta = 2*pi*delta_hz
    Kappa = 2*pi*kappa_hz
    Gamma = 2*pi*split_hz
    return -hbar*(128.0*g**2*sbar*sbard*Delta*Eta*Kappa**2*(-5*Gamma**6 + (4*Delta**2 +Kappa**2)**3 + 8*(-16*Delta**4 +Kappa**4)*Omega**2+\
16*(4*Delta**2 + Kappa**2)*Omega**4 + Gamma**4*(-20*Delta**2 - 9*Kappa**2 + 24*Omega**2) + Gamma**2*(144*Delta**4 -3*Kappa**4 - 16*Omega**4 +8*Delta**2*(3*Kappa**2 -8*Omega**2))))/\
(m*(Gamma**4 + 2*Gamma**2*(-4*Delta**2 + Kappa**2) + (4*Delta**2 + Kappa**2)**2)*(Kappa**2 + (Gamma + 2*Delta - 2*Omega)**2)*(Kappa**2 + (Gamma - 2*Delta + 2*Omega)**2)*(Kappa**2 + (Gamma - 2*(Delta + Omega))**2)*(Kappa**2 + (Gamma + 2*(Delta + Omega))**2))


def deltaOmega(delta_hz,kappa_hz = Kappa/(2*pi),split_hz = Gamma/(2*pi),sbar=sbar):
    """parameters should be in Hz!!!"""
    sbard = sbar
    Delta = 2*pi*delta_hz
    Kappa = 2*pi*kappa_hz
    Gamma = 2*pi*split_hz
    return (16*g**2*sbar*sbard*Delta*Eta*Kappa*(-3*Gamma**8 + 4*Gamma**6*(8*Delta**2 - 2*Kappa**2 + 7*Omega**2) + 4*Gamma**2*Omega**2*(-48*Delta**4 - 40*Delta**2*Kappa**2 + 9*Kappa**4 +8*(4*Delta**2 + Kappa**2)*Omega**2 +16*Omega**4) + (4*Delta**2 +Kappa**2)*(Kappa**2 + 4*(Delta - Omega)**2)*(4*Delta**2 +Kappa**2 - 4*Omega**2)*(Kappa**2 +4*(Delta + Omega)**2) - 2*Gamma**4* (48*Delta**4 + 3*Kappa**4 - 30*Kappa**2 *Omega**2 + 40*Omega**4 + 8*Delta**2*(-Kappa**2 + Omega**2)))*hbar)/(m*(Gamma**4 + 2*Gamma**2*(-4*Delta**2 + Kappa**2) + (4*Delta**2 + Kappa**2)**2)*(Kappa**2 + (Gamma +2*Delta - 2*Omega)**2)*Omega*(Kappa**2 + (Gamma-2*Delta + 2*Omega)**2)*(Kappa**2 + (Gamma - 2*(Delta + Omega))**2)*(Kappa**2 + (Gamma + 2*(Delta + Omega))**2))


