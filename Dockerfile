FROM python:3.10

ADD . .

RUN pip install -r requirements.txt

CMD ["python", "/frontend/start_gui.py"]

