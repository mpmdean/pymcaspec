import PyMca5.PyMcaCore.SpecFileDataSource as SpecFileDataSource
import numpy as np
from matplotlib import pyplot as plt
from itertools import cycle

marker_cycle = cycle(['o', 's', 'p', 'h', 'd', 'v', '^', '>', '<'])


class scan:
    """Container for scan in spec file"""
    def __init__(self, dataobject_list):
        """ Class initialization

        Parameters
        ----------
        dataobject_list :  list of PyMca5.PyMcaCore.DataObject.DataObject
            The scan contains these dataobjects/keys
        """
        self.dataobjects = [dataobject for dataobject in dataobject_list]

    def get_description(self):
        """Make string describing motors.
        This is useful for indexing motors.

        Returns
        ----------
        motors_description : string
            Description of the motors that were scanned and that were recorded
            as a baseline.
        """
        motors_description = ''
        for dataobject in self.dataobjects:
            PrimaryNames = dataobject.info['LabelNames']
            BaselineNames = dataobject.info['MotorNames']
            if type(BaselineNames) is not list:
                BaselineNames = ['no baseline motors']
            motors_description += ("Key: {}\n".format(dataobject.info['Key']) +
                                   "Scanned Motors are:\n{}\n".format(
                                   "\t".join(PrimaryNames)) +
                                   "Baseline Motors are:\n{}\n\n".format(
                                   "\t".join(BaselineNames))
                                   )
        return motors_description

    def __str__(self):
        return self.get_description()

    def __repr__(self):
        return self.get_description()

    def index(self, key):
        """Index a particular key (motor) from the scan.

        Parameters
        ----------
        key : integer or string
            Integers label the columns to return 0, 1, 2 etc.
            Strings give the name of the scanned motor to index from the scan.

        Returns
        ----------
        datacol : numpy array
            1D array of data corresponding to key
        """
        try:
            datacol = np.hstack([dataobject.data[:, key]
                                 for dataobject in self.dataobjects])
        except IndexError:
            PrimaryNames = self.dataobjects[0].info['LabelNames']
            try:
                index = [i for i, k in enumerate(PrimaryNames) if key == k][0]
                datacol = np.hstack([dataobject.data[:, index]
                                    for dataobject in self.dataobjects])
            except IndexError:
                raise IndexError("key {} not found".format(key))

        return datacol

    def get_baseline(self, key):
        """Index a particular baseline value.

        Parameters
        ----------
        key : string
            The name of the baseline (i.e. non scanned)
            motor to index from the scan.

        Returns
        ----------
        motor_val : float or list of floats
            The values of the motor corresponding to key
            for each scan in the series.

        """
        MotorNames = self.dataobjects[0].info['MotorNames']
        try:
            index = [i for i, k in enumerate(MotorNames) if key == k][0]
        except IndexError:
            raise IndexError("key {} not found".format(key))

        if len(self.dataobjects) > 1:
            motor_val = [dataobject.info['MotorValues'][index]
                         for dataobject in self.dataobjects]
        else:
            motor_val = self.dataobjects[0].info['MotorValues'][index]

        return motor_val

    def __getitem__(self, key):
        """Assign [] indexing method to try to return data
        associated with a key."""
        return self.index(key)

    def __iter__(self):
        """Iterating returns scan objects corresponding
        to individual scans."""
        for d in self.dataobjects:
            yield scan([d])

    def plot(self, ax=None, xkey=0, ykey=-1, monitor=None, **kwargs):
        """Create x,y plot of the scan data.
        This creates one line per scan.
        If xkey is not specified it is assumed to be index 0
        If ykey is not specified it is assumed to be the last index.
        label can be passed to override the legend label.
        Otherwise it is the scan name or key.

        Parameters
        ----------
        xkey : integer or string
            key for independent axis data
        ykey : integer or string
            key for depependent axis data
        monitor : string
            key for monitor, which is used to divide y
        kwargs :
            Key word arguments are passed to ax.plot()

        Returns
        --------
        leg : matplotlib legend object
            Last legend created in the plot
        art : matplotlib artist
            Last artist object created in plot
        ax : matplotlib axis
            axis that contains the plotted data
        """
        if ax is None:
            _, ax = plt.subplots()

        if isinstance(xkey, int):
            xkey = self.dataobjects[0].info['LabelNames'][xkey]

        if isinstance(xkey, int):
            xkey = self.dataobjects[0].info['LabelNames'][xkey]

        for s in self:
            try:
                leg, art, ax = s.plot_combined(ax=ax, xkey=xkey, ykey=ykey,
                                               monitor=monitor, **kwargs)
            except IndexError:
                k = s.dataobjects[0].info['Key']
                info = '{} and {} in scan {}'.format(xkey, ykey, k)
                raise IndexError('Tried to index ' + info)

        return leg, art, ax

    def get_hkl(self):
        """Get hkl value of scans

        returns
        --------
        hkl : tuple or list of tuples
            (h, k, l) or a list of (h, k, l) values
            depending on whether all scans have the same value.
        """
        hkls = [d.info['hkl'] for d in self.dataobjects]
        if all(h == hkls[0] for h in hkls):
            hkl = hkls[0]
        else:
            raise Warning("Different scans have different (h, k, l) values")
            hkl = hkls

        return hkl


    def plot_combined(self, ax=None, xkey=0, ykey=-1, monitor=None, **kwargs):
        """Create x,y plot of the scan data.
        This creates one line.
        If xkey is not specified it is assumed to be index 0
        If ykey is not specified it is assumed to be the last index.
        label can be passed to override the legend label.
        Otherwise it is the scan name or key.

        Parameters
        ----------
        xkey : integer or string
            key for independent axis data
        ykey : integer or string
            key for depependent axis data
        monitor : string
            key for monitor, which is used to divide y
        kwargs :
            Key word arguments are passed to ax.plot()

        Returns
        --------
        leg : matplotlib legend object
            The legend created in the plot
        art : matplotlib artist
            artist object created in plot
        ax : matplotlib axis
            axis that contains the plotted data
            """
        xdata = self.index(xkey)
        ydata = self.index(ykey)

        if isinstance(xkey, int):
            xkey = self.dataobjects[0].info['LabelNames'][xkey]

        if isinstance(ykey, int):
            ykey = self.dataobjects[0].info['LabelNames'][ykey]

        if ax is None:
            _, ax = plt.subplots()

        if 'label' in kwargs.keys():
            label = kwargs.pop('label')
        else:
            label = [d.info['Key'] for d in self.dataobjects]

        if monitor is None:
            monitor = ''
        else:
            ydata /= self.index(monitor)
            monitor = "/" + monitor

        if 'marker' not in kwargs.keys():
            kwargs.update({'marker': next(marker_cycle)})

        art = ax.plot(xdata, ydata, **kwargs,
                      label="{}".format(label))

        ax.set_xlabel('{}'.format(xkey))
        ax.set_ylabel('{}'.format(ykey+monitor))
        leg = ax.legend()

        return leg, art, ax


class specfile:
    """Container for specfile"""
    def __init__(self, filename):
        """Initialize class

        Parameters
        ----------
        filename : string
            Path to the spec file
        """
        self.filename = filename
        self.source = SpecFileDataSource.SpecFileDataSource(filename)

    def get_description(self):
        """Make string showing file header and number of scans

        Returns
        ----------
        file_desc : string
            File size and header
        """
        self.size = self.source.getSourceInfo()['Size']
        header = str(self.source.getSourceInfo()['FileHeader'])
        file_desc = "Specfile {}\n {} scans\n{}".format(self.filename,
                                                        self.size, header)
        return file_desc

    def keys(self):
        """Get all the keys

        Returns
        keys : list
            List of all keys in the keyfile
        """
        return self.source.getSourceInfo()['KeyList']

    def __str__(self):
        return self.get_description()

    def __repr__(self):
        return self.get_description()

    def index(self, key):
        """Index a particular scan file.

        Parameters
        ----------
        key : string
            The name scan to index from the specfile. usually '5.1'
            If a number is passed it will be converted to stringself.
            If the indexing fails the string will be appended by '.1'

        Returns
        ----------
        dataobject : PyMCA dataobject
            A single dataobject from the specfile
        """
        try:
            dataobject = self.source.getDataObject(key)
        except (KeyError, AttributeError):
            key = str(key)
            if '.' not in key:
                key += '.1'
            try:
                dataobject = self.source.getDataObject(key)
            except (KeyError, AttributeError, SyntaxError):
                keys = self.keys()
                found_keys = [k for k in keys if key is k]
                if len(found_keys) == 1:
                    dataobject = self.source.getDataObject(found_keys[0])
                elif len(found_keys) > 1:
                    msg = ("key {} matches multiple ".format(key) +
                           "entries in file:\n{}".format(found_keys))
                    raise IndexError(msg)
                elif len(found_keys) == 0:
                    raise IndexError("key {} not found".format(key))
        return dataobject

    def get_MCA(self, key):
        """Get MCA data

        Params
        ------
        key : string
            key for source following the rules below
            e.g. 1.1.1

        Returns
        ------
        data : array
            data array
        """
        do = self.source._getMcaData(key)
        data = do.data

        return data


    def get_all_MCA(self):
        """Get all the MCA data for channel 1

        Params
        ------
        key : string
            key for source following the rules below
            e.g. 1.1.1

        Returns
        ------
        dataset : array
            dat
        """
        dataset = np.array([self.get_MCA(key + '.1') for key in self.keys()])
        return dataset

    def __getitem__(self, keys):
        """Assign [] indexing method to try to index scan class instance.

        Parameters
        ----------
        keys : list of keys to index specfile
            The name scan to index from the specfile.
            Key usually are of the form '5.1' or similar.
            If a number is passed it will be converted to stringself.
            If the indexing fails the string will be appended by '.1'
            If a single string, float or integer is passed it will be
            converted to a list

        Returns
        -----
        S : instance of scan class

        """

        # If keys indexes directly use that
        try:
            return scan([self.index(keys)])
        except (KeyError, SyntaxError, AttributeError, IndexError, ValueError):
            pass

        # If keys is slice make an interable
        if type(keys) == slice:
            if keys.step is None:
                keys = range(keys.start, keys.stop)
            else:
                keys = range(keys.start, keys.stop, keys.step)
        # Then try to interate over keys
        return scan([self.index(key) for key in keys])

    # Append info to get_MCA docustring
    from PyMca5.PyMcaCore.SpecFileLayer import SpecFileLayer
    alldoc = SpecFileLayer.LoadSource.__doc__
    adddoc = alldoc.split("valid for ScanType==SCAN or MESH or MCA")[1]
    get_MCA.__doc__ += adddoc
