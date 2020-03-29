FROM python:3

ADD requirements.txt /
RUN pip install -r /requirements.txt

ADD src /code

CMD ["python", "/code/Runner.py"]