FROM jupyter/scipy-notebook:cf6258237ff9

RUN pip install --upgrade pip
RUN pip install --user numpy fisx h5py cython
RUN pip install --user pymca --no-binary 

RUN pip install --user pymcaspec
