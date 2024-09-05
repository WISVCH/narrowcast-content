# start by pulling the python image
FROM python:3.12-alpine

# copy every content from the local file to the image
COPY . /app

# switch working directory
WORKDIR /app

# install the dependencies and packages
RUN pip install .

EXPOSE 8080

CMD [ "python", "-m", "narrowcast_content.waitress_server"]