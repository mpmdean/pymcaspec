# pymcaspec
Wrapper around PyMca for parsing spec files

This is dependent on the PyMca package
https://github.com/vasole/pymca

See the notebook for examples

# Installation
```
pip install PyMca5  
git clone https://github.com/mpmdean/pymcaspec.git  
cd pymcaspec  
python setup.py install
``` 
# Additional installation
```
conda install jupyterlab
```
and install https://github.com/matplotlib/jupyter-matplotlib following the instructions to have interactive plots.  

# Basic usage 
create specfile object  
```
from pymcaspec import specfile
F = specfile('<name of file>')
```

To show the relevent details of the file call  
```
print(F)
```

The specfile instance can be indexed to create scan objects. Either from a single scan index  
```
S = F['5.1']  
```
or from a series of scans 
```
S = F[['5.1', '7.1', '8.1']]
```

Calling  
```
S = F[3:6]  
```
Assumes that you want the first '.1' scan and returns keys '3.1', '4.1', '5.1'

The code assumes that these keys include the same set of scanned motors. Otherwise it will fail. If the combination fails it likely means that it does not make sense to combine the keys. 

call  
```
print(S)  
```
to show a summary of the scanned and baseline motors. 

The motors can be accessed by indexing their names as   
```
H = S['H']  
I = S['APD']  
```
or using the column number starting from zero.   
```
H = S[0]  
I = S[-1] 
```
Non-scanned (baseline) motors are accessed as  
```
S.get_baseline('chi')
```

```
S.plot()
```
will plot the data. 


Examples are shown in more detail in the ipython notebooks.
