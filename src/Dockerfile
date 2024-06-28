FROM python:3.9
RUN apt-get update -y
RUN apt-get upgrade -y

# set work directory
WORKDIR /src

# install dependencies
RUN python -m pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# copy project
COPY ./app ./app

# run project
CMD ["python3", "./app/manage.py", "runserver", "0.0.0.0:8000"]