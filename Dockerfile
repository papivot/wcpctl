FROM python:3

WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY wcpctl.py /app/wcpctl.py
RUN pip install -r requirements.txt

ENTRYPOINT [ "./wcpctl.py" ]