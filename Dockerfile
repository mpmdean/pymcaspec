FROM jupyter/scipy-notebook
RUN pip install --upgrade pip \
    && pip install numpy fisx h5py \
    && pip install pymca \
    &&  pip install pymcaspec
