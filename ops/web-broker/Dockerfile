FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258
# Immutable Debian snapshot, fixed iptables; final image ID is recorded by the build helper.
RUN printf 'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/20261015T000000Z bookworm main\n' > /etc/apt/sources.list \
    && rm -f /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::Check-Valid-Until=false update \
    && apt-get install -y --no-install-recommends iptables=1.8.9-2 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /broker
COPY web_policy.py worker.py /broker/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-E", "-s", "/broker/worker.py"]
