FROM python:3
RUN pip install --no-cache-dir pygithub
COPY tada.py /tada.py
ENTRYPOINT ["python" "/tada.py"]
