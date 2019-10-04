FROM jupyter/scipy-notebook:cf6258237ff9
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

RUN pip install --upgrade pip \
    && sudo apt-get install python3-dev \
    && pip install numpy fisx h5py \
    && pip install pymca \
    &&  pip install pymcaspec
