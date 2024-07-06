FROM python:3.9
ENV PYTHONUNBUFFERED=1

# set work directory
WORKDIR /src

# install dependencies
RUN python -m pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# copy project
COPY ./app ./app
COPY ./start.sh ./start.sh