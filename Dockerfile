FROM jupyter/scipy-notebook:cf6258237ff9
RUN pip install --upgrade pip
RUN pip install numpy fisx h5py
RUN pip install pymca
RUN pip install pymcaspec
