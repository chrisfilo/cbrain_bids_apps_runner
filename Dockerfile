FROM continuumio/miniconda:4.3.27

RUN pip install pybids==0.4.2

RUN mkdir /code /inputs /outputs
COPY run.py /code/run.py

WORKDIR /outputs

ENTRYPOINT ["python", "/code/run.py"]