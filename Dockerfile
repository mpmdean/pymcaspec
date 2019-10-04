FROM jupyter/scipy-notebook:cf6258237ff9

# Copy repo into ${HOME}, make user own $HOME
USER root
COPY . ${HOME}
RUN chown -R ${NB_USER} ${HOME}
USER ${NB_USER}

USER root
RUN apt-get install -y mesa-common-dev libglu1-mesa-dev freeglut3-dev
USER ${NB_USER}

RUN pip install --upgrade pip
RUN pip install --user numpy fisx h5py cython
RUN pip install --user --no-binary :all: PyMca5
RUN pip install --user --no-binary :all: pymcaspec
