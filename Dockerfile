FROM jupyter/scipy-notebook:cf6258237ff9

RUN apt-get install -y sudo
RUN apt-get install -y mesa-common-dev libglu1-mesa-dev freeglut3-dev
RUN pip install --upgrade pip
RUN pip install --user numpy fisx h5py cython
RUN pip install --user --no-binary :all: PyMca5
RUN pip install --user --no-binary :all: pymcaspec
