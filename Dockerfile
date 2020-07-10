FROM jdocker pull jupyter/scipy-notebook@sha256:3a2b07f1919199785048b2230d98f11ad7a1ca914b17e1d722b6ea25c461af64

# Copy repo into ${HOME}, make user own $HOME
USER root
COPY . ${HOME}
RUN chown -R ${NB_USER} ${HOME}

RUN sudo apt-get update
RUN apt-get install -y mesa-common-dev libglu1-mesa-dev
USER ${NB_USER}

RUN pip install --upgrade pip
RUN pip install --user numpy fisx h5py cython
RUN pip install --user --no-binary :all: PyMca5
RUN python setup.py install 
