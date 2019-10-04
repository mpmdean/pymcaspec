FROM jupyter/scipy-notebook:cf6258237ff9

ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"

USER root

RUN pip install --upgrade pip
RUN pip install numpy fisx h5py cython
RUN pip install pymca

RUN pip install pymcaspec
