FROM python:3.10-slim-buster

WORKDIR /app

COPY pip_requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY veeam_exporter_src/. .

EXPOSE 9247/tcp

ENTRYPOINT [ "python3", "t.py"]