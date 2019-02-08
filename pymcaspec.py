import PyMca5.PyMcaCore.SpecFileDataSource as SpecFileDataSource
import numpy as np

class scan:
    """Container for scan in spec file"""
    def __init__(self, dataobject_list):
        """ Class initialization

        Parameters
        ----------
        dataobject_list :  list of PyMca5.PyMcaCore.DataObject.DataObject
            List of scan container from PyMCA
        """
        self.dataobjects = [dataobject for dataobject in dataobject_list] 

    def __str__(self):
        """Print method shows motors.
        This is useful for indexing motors.

        Returns
        ----------
        motors_description : string
            Description of the motor
        """
        motors_description = ''
        for dataobject in self.dataobjects:
            PrimaryNames = dataobject.info['LabelNames']
            BaselineNames = dataobject.info['MotorNames']
            motors_description += ("Key: {}\n".format(dataobject.info['Key']) +
                                   "Scanned Motors are:\n{}\n".format("\t".join(PrimaryNames)) +
                                   "Baseline Motors are:\n{}\n\n".format("\t".join(BaselineNames)))
        return motors_description

    def index(self, key):
        """Index a particular key (motor) from the scan.

        Parameters
        ----------
        key : string
            The name of the scanned motor to index from the scan.

        Returns
        ----------
        datacol : numpy array
            1D array of data corresponding to key
        """
        PrimaryNames = self.dataobjects[0].info['LabelNames']
        try:
            index = [i for i, k in enumerate(PrimaryNames) if key == k][0]
        except:
            raise Exception("key {} not found".format(key))

        datacol = np.hstack([dataobject.data[:,index]
                             for dataobject in self.dataobjects])
        return datacol

    def get_baseline(self, key):
        """Index a particular baseline value.

        Parameters
        ----------
        key : string
            The name of the baseline (i.e. non scanned) motor to index from the scan.

        Returns
        ----------
        motor_val : float or list of floats
            The values of the motor corresponding to key for each scan in the series.

        """
        MotorNames = self.dataobjects[0].info['MotorNames']
        try:
            index = [i for i, k in enumerate(MotorNames) if key == k][0]
        except:
            raise Exception("key {} not found".format(key))

        if len(self.dataobjects) > 1:
            motor_val = [dataobject.info['MotorValues'][index]
                         for dataobject in self.dataobjects]
        else:
            motor_val =  self.dataobjects[0].info['MotorValues'][index]
            
        return motor_val

    def __getitem__(self, key):
        """Assign [] indexing method to try to return data associated with a key."""
        return self.index(key)


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
        self.source =  SpecFileDataSource.SpecFileDataSource(filename)

    def __str__(self):
        """Print method shows file header and number of scans

        Returns
        ----------
        file_description : string
            File size and header
        """
        self.size = self.source.getSourceInfo()['Size']
        header = str(self.source.getSourceInfo()['FileHeader'])
        file_description = "Specfile {}\n {} scans\n{}".format(self.filename, self.size, header)
        return file_description

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
        except:
            key = str(key)
            if '.' not in key:
                key += '.1'
            try:
                dataobject = self.source.getDataObject(key)
            except:
                keys = self.source.getSourceInfo()['KeyList']
                found_keys = [k for k in keys if key is k]
                if len(found_keys) == 1:
                    dataobject = self.source.getDataObject(found_keys[0])
                elif len(found_keys) > 1:
                    raise Exception("key {} matches multiple entries in file:\n{}".format(key, found_keys))
                elif len(found_keys) == 0:
                    raise Exception("key {} note found".format(key))
        return dataobject

    def __getitem__(self, keys):
        """Assign [] indexing method to try to scan classe instqnc.
        
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
        except:
            pass
        
        # If keys is slice make an interable
        if type(keys) == slice:
            if keys.step == None:
                keys = range(keys.start, keys.stop)
            else:
                keys = range(keys.start, keys.stop, keys.step)
        # Then try to interate over keys
        return scan([self.index(key) for key in keys])

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