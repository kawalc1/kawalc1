FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN mkdir /kawalc1

WORKDIR /kawalc1

ADD requirements.txt /kawalc1/requirements.txt
RUN pip install -r requirements.txt

ADD mengenali /kawalc1/mengenali
ADD kawalc1 /kawalc1/kawalc1
ADD static /kawalc1/static
ADD manage.py /kawalc1/manage.py
ADD __init__.py /kawalc1/__init__.py
RUN mkdir /kawalc1/static/extracted && mkdir /kawalc1/static/upload && mkdir /kawalc1/static/transformed

ADD . /kawalc1/

CMD ["/kawalc1/manage.py", "runserver", "0.0.0.0:8000"]

