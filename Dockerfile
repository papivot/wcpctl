FROM python:3

WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY src/ /app/src
COPY wcpctl /app/wcpctl
RUN pip install -r requirements.txt

ENTRYPOINT [ "./wcpctl" ]