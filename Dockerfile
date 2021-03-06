FROM jupyter/scipy-notebook:862de146632b

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
