# pymcaspec
Wrapper around PyMca for parsing spec files

This is dependent on the PyMca package
https://github.com/vasole/pymca

See the notebook for examples

# Basic usage 
create specfile object  
F = specfile('LO_20180704')

To show the relevent details of the file run  
print(F)

This can be indexed to create scan objects. Either from a single scan index  
S = F['5.1']  
or from a series of scans  
S = F[['5.1', '7.1', '8.1']]

Calling  
S = F[3:6]  
Assumes that you want the first '.1' scan and returns keys '3.1', '4.1', '5.1'

If you request data with different scanned motors is combined this may fail. 

call  
print(S)  
to show a summary of the scanned and baseline motors. 

The motors can be accessed by indexing this  
H = S['H']  
I = S['APD']  


Non-scanned (baseline) motors are accessed as  
S.get_baseline('chi')


S.plot()
will plot the data. 


Examples are shown in more detail in the ipython notebooks.