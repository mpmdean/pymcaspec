FROM jupyter/scipy-notebook:cf6258237ff9
RUN pip install --upgrade pip \
    && pip install numpy fisx h5py \
    && pip install pymca \
    &&  pip install pymcaspec \
 
