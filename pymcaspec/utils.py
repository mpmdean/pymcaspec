import numpy as np


def get_T_ISR(scan_inst):
    """ISR specific function to read the temperature.

    Parameters
    ----------
    scan_inst : instance of scan class
        a particular scan created in pymcaspec

    Returns
    -------
    TB : float
        The B temperature sensor
    TA : float
        The A temperature sensor
    """
    TB, TA = [], []
    for dataobject in scan_inst.dataobjects:
        header = dataobject.info['Header']
        lineX = [line for line in header if '#X' in line][0]
        tb, ta = lineX.split(' ')[1:4:2]
        TB.append(float(tb))
        TA.append(float(ta))

    return np.array(TB), np.array(TA)


def get_merixE(F):
    """Read out the values of merixE of sector 27 style MYT E_dataset

    Parameters
    ----------
    F : specfile instance
        The specfile loaded as specfile(<filename>)

    Returns
    -------
    merixE : array
        All the merix energies

    """
    def get_energy_val(key):
        val = next(float(line[4:])
                   for line in F.source.getDataObject(key).info['Header']
                   if line[:3] == '#PV')
        return val

    merixE = np.array([get_energy_val(key) for key in F.keys()])
    return merixE


def calculate_energy_per_pixel(d, R, energy_edge, mmsperchannel=50e-3):
    """Compute the energy per Mythen Channel

    Parameters
    ----------
    d : float
        Lattice spacing in Angstroms
    R : float
        Analyer distance in mm
    energy_edge : float
        Energy of the edge in keV
    mmsperchannel = 50e-3  #mm

    Returns
    --------
    energy_per_pixel : float
        Energy per Mythen channel in keV
    """
    hbarc = 2*np.pi*1.973269718  # keV/A
    energy_backscattering = hbarc/(2*d)  # keV
    thetaBragg = np.arcsin(energy_backscattering/energy_edge)  # rad
    energy_per_pixel = ((energy_edge*mmsperchannel)
                        / (2*R*np.tan(thetaBragg)))
    return energy_per_pixel


def clean_mythen_data(mythen_dataset, min_chan, max_chan, threshold):
    """Set pixels to zero based on channel range and threshold
    Parameters
    ---------
    mythen_dataset  : array
        The data in shape (pixels,  channels)
    min_chan : integer
        Minimum channel -- those below this are set to zero
    max_chan : integer
        Minimum channel -- those below this are set to zero
    threshold : float
        set values above this to zero

    Returns
    -------
    mythen_dataset  : array
        The data in shape (pixels,  channels) after cleaning
    """
    indices = np.arange(1, mythen_dataset.shape[1] + 1)
    choose = np.logical_or(indices < min_chan, indices > max_chan)
    mythen_dataset[:, choose] = 0
    mythen_dataset[:, choose] = 0
    mythen_dataset[mythen_dataset > threshold] = 0
    return mythen_dataset


def construct_E_M(central_Es, central_Ms, mythen_dataset,
                  magicchannel, energy_per_pixel):
    """Create energy and monitor values
    corresponding to the a mythen_dataset

    Parameters
    ----------
    central_Es : array
        The energy of the magicchannel for each mythen readout in keV
    central_Ms : array
        The monitor for each mythen readout
    mythen_dataset  : array
        The mythen data in shape (pixels,  channels)
        This is used to determine the number of channels
    magicchannel : float
        The magic rerference channel on the mythen
    energy_per_pixel  : float
        Energy per Mythen channel in keV

    Returns
    -------
    E_dataset : array
        Energy for each pixel with the shape
        as mythen_dataset
    M_dataset : array
        Monitor for each pixel with the shape
        as mythen_dataset
    """
    indices = np.arange(1, mythen_dataset.shape[1]+1)
    E_dataset = []
    M_dataset = []
    for central_E, central_M in zip(central_Es, central_Ms):
        E_array = energy_per_pixel*(magicchannel - indices) + central_E

        E_dataset.append(E_array)
        M_dataset.append(indices*0 + central_M)

    E_dataset = np.array(E_dataset)
    M_dataset = np.array(M_dataset)
    return E_dataset, M_dataset


def bin_mythen(E_dataset, M_dataset, mythen_dataset,
               bin_edges):
    """
    Bin the mythen data. np.NaN values will be ignored.

    Parameters
    ---------
    E_dataset : array
        Energy for each pixel with the shape
        as mythen_dataset
    M_dataset : array
        Monitor for each pixel with the shape
        as mythen_dataset
    mythen_dataset  : array
        The mythen data in shape (pixels,  channels)
    bin_edges : array or None
        The energy bin edges for the binning

    returns
    -------
    E : array
        Energies coresonding to bin centers
    I : array
        Intensities
    M : array
        Montior
    N : array
        Number of contributing mythen pixels
    """
    E_all = E_dataset.ravel()
    I_all = mythen_dataset.ravel()
    M_all = M_dataset.ravel()

    keep_indices = np.logical_and.reduce([np.isfinite(E_all),
                                          np.isfinite(I_all),
                                          np.isfinite(M_all)])

    E_all = E_all[keep_indices]
    I_all = I_all[keep_indices]
    M_all = M_all[keep_indices]

    I, _ = np.histogram(E_all, bins=bin_edges, weights=I_all)
    M, _ = np.histogram(E_all, bins=bin_edges, weights=M_all)

    N, _ = np.histogram(E_all[I_all > 0], bins=bin_edges)
    
    E = (bin_edges[:-1] + bin_edges[1:])/2
    return E, I, M, N


def bin_RIXS(central_Es, central_Ms, mythen_dataset,
             magicchannel, energy_per_pixel,
             min_chan=-np.inf, max_chan=np.inf, threshold=np.inf, bin_edges=None):
    """Create a RIXS spectrum from sector 27 data

    Parameters
    ----------
    central_Es : array
        The energy of the magicchannel for each mythen readout in keV
    central_Ms : array
        The monitor for each mythen readout
    mythen_dataset  : array
        The mythen data in shape (pixels,  channels)
        This is used to determine the number of channels
    magicchannel : float
        The magic rerference channel on the mythen
    energy_per_pixel  : float
        Energy per Mythen channel in keV
    bin_edges : array or None
        The energy bin edges for the binning
        If none it will be constructed based on the data.
    min_chan : integer
        Minimum channel -- those below this are set to zero
    max_chan : integer
        Minimum channel -- those below this are set to zero
    threshold : float
        set values above this to zero


    returns
    -------
    E : array
        Energies coresonding to bin centers
    I : array
        Intensities
    M : array
        Montior
    """
    if bin_edges is None:
        step = np.mean(np.abs(np.diff(central_Es)))
        full_E_range = np.concatenate([[central_Es.min() - step],
                                       central_Es,
                                       [central_Es.max() + step]])
        
        bin_edges = (full_E_range[:-1] + full_E_range[1:])/2

    mythen_dataset = clean_mythen_data(mythen_dataset,
                                       min_chan, max_chan, threshold)

    E_dataset, M_dataset = construct_E_M(central_Es, central_Ms,
                                         mythen_dataset, magicchannel, energy_per_pixel)

    E, I, M, N = bin_mythen(E_dataset, M_dataset, mythen_dataset,
                            bin_edges)
    return E, I, M, N
