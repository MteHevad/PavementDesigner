import numpy as np
from scipy.optimize import fsolve

def predict_pavement_esal(z, so, sn, psi, mr):
    """
    Generate a prediction for Equivalent Single Axle Load (ESAL) based on given parameters.

    Parameters:
    z (float): standard deviation (usually 0.5-0.999)
    so (float): standard error (usually 0.4-0.5 for asphalt, 0.35-0.4 for concrete)
    sn (float): structural number
    psi (float): allowable delta in serviceability index (usually 1.0-3.0)
    mr (float): resilient modulus

    Returns:
    float: the predicted ESAL value
    """
    right_side = z*so+9.36*np.log10(sn+1)-0.2*(np.log10(psi/(4.2-1.5))/(0.4+1094/(sn+1)**0.519))+2.32*np.log10(mr)-8.07
    esals = 10**right_side
    return esals

def solve_sn(z, so, psi, mr, esal):
    def f(sn):
        val = sn[0]
        return predict_pavement_esal(z, so, val, psi, mr) - esal
    return fsolve(f, np.array([3]))[0]

def serviceability_loss_factor(pt):
    return np.log10((4.2-pt)/(4.2-1.5))

def serviceability_given_axle_load(kip, axles, sn):
    pt = 0.4+((0.081*(kip+axles)**3.23)/((sn+1)**5.19*axles**3.23))
    return pt

def flexible_equivalent_single_axle_load(weight, axles, pt, sn):
    kip = weight/1000
    loading = ((18+1)/(kip + axles))**4.79
    loss_factor = serviceability_loss_factor(pt)
    bx = serviceability_given_axle_load(kip, axles, sn)
    b18 = serviceability_given_axle_load(18, 1, sn)
    factor = loading*(10**(loss_factor/bx)/10**(loss_factor/b18))*axles**4.33
    return factor**-1

def total_trips(adt, years, growth):
    base_trips = np.full(years, 365*adt)
    years = np.arange(years)
    growth = np.array([(1+growth)**y for y in years])
    return np.sum(base_trips*growth)

def trips_to_esals(trips, direction_factor, lane_factor, equivalent_load):
    return direction_factor*lane_factor*equivalent_load*trips


def estimate_resilient_modulus_from_R(r):
    return 1000+555*r

def estimate_resilient_modulus_from_CBR(cbr):
    return 2555*cbr**0.64


