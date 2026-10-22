FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258
COPY requirements.txt /parser/requirements.txt
RUN pip install --no-cache-dir --no-deps --require-hashes -r /parser/requirements.txt
COPY worker.py /parser/worker.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 65534:65534
WORKDIR /parser
ENTRYPOINT ["python", "-I", "/parser/worker.py"]
