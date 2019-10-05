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


def calculate_dEdChan(d, R, edgeEn, mmsperchannel=50e-3):
    """Compute the energy per Mythen Channel

    Parameters
    ----------
    d : float
        Lattice spacing in Angstromes
    R : float
        Analyer distance in mm
    edgeEn : float
        Energy of the edge in keV
    mmsperchannel = 50e-3  #mm

    Returns
    --------
    dEdchan : float
        Energy per Mythen channel in keV
    """
    hbarc = 2*np.pi*1.973269718  # keV/A
    EB = hbarc/(2*d)  # backscattering energy (keV)
    thetaB = np.arcsin(EB/edgeEn)  # analyzer theta Bragg angle in rad
    dEdr = (edgeEn/(2*R))/np.tan(thetaB)  # keV/mm
    dEdchan = dEdr*mmsperchannel  # keV/channel
    return dEdchan


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
    mythen_dataset[:, :min_chan] = 0
    mythen_dataset[:, max_chan:] = 0
    mythen_dataset[mythen_dataset > threshold] = 0
    return mythen_dataset


def construct_E_M(central_Es, central_Ms, mythen_dataset,
                  magicchannel, dEdchan):
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
    dEdchan  : float
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
        E_array = dEdchan*(magicchannel-indices) + central_E

        E_dataset.append(E_array)
        M_dataset.append(indices*0 + central_M)

    E_dataset = np.array(E_dataset)
    M_dataset = np.array(M_dataset)
    return E_dataset, M_dataset


def bin_mythen(E_dataset, M_dataset, mythen_dataset,
    bin_edges=None, binstep=None):
    """
    Bin the mythen data

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
        If none it will be constructed based on the data and binstep
    binstep : float
        The energy difference between different points for binning

    returns
    -------
    E : array
        Energies coresonding to bin centers
    I : array
        Intensities
    M : array
        Montior
    """
    E_all = E_dataset.ravel()
    I_all = mythen_dataset.ravel()
    M_all = M_dataset.ravel()

    if bin_edges is None:
        bin_edges = np.arange(E_all.min()-binstep/2 - 1e-6,
                              E_all.max()+binstep/2 + 1e-6,
                              binstep)

    E = (bin_edges[1:] + bin_edges[:-1])/2
    I, _ = np.histogram(E_all, bins=bin_edges, weights=I_all)
    M, _ = np.histogram(E_all, bins=bin_edges, weights=M_all)

    choose = I > 0
    E = E[choose]
    I = I[choose]
    return E, I, M


def bin_RIXS(central_Es, central_Ms, mythen_dataset,
             magicchannel, dEdchan,
             min_chan, max_chan, threshold,
             bin_edges=None, binstep=None):
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
    dEdchan  : float
        Energy per Mythen channel in keV
    min_chan : integer
        Minimum channel -- those below this are set to zero
    max_chan : integer
        Minimum channel -- those below this are set to zero
    threshold : float
        set values above this to zero
    bin_edges : array or None
        The energy bin edges for the binning
        If none it will be constructed based on the data and binstep
    binstep : float
        The energy difference between different points for binning

    returns
    -------
    E : array
        Energies coresonding to bin centers
    I : array
        Intensities
    M : array
        Montior
    """
    mythen_dataset = clean_mythen_data(mythen_dataset,
                                       min_chan, max_chan, threshold)

    E_dataset, M_dataset = construct_E_M(central_Es, central_Ms,
                                         mythen_dataset, magicchannel, dEdchan)

    E, I, M = bin_mythen(E_dataset, M_dataset, mythen_dataset,
                         bin_edges=bin_edges, binstep=binstep)
    return E, I, M
