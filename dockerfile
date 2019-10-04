FROM jupyter/scipy-notebook:cf6258237ff9
RUN pip install numpy \
    && pip install pymca
    &&  pip install pymcaspec\
 
