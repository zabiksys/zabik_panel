FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /

# The environment variable ensures that the python output is set straight
# to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
   dpkg-dev \
   gcc \
   git \
   curl \
   gnupg \
   unixodbc-dev \
   libgssapi-krb5-2

# https://docs.microsoft.com/es-es/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15
# Workaround for Microsoft driver not available for Debian Bullseye (11)
# https://github.com/MicrosoftDocs/sql-docs/issues/6494
RUN apt-get -y update \
    && apt-get -y install equivs \
    && echo 'Package: multiarch-support-dummy\nProvides: multiarch-support\nDescription: Fake multiarch-support' > multiarch-support-dummy.ctl \
    && equivs-build multiarch-support-dummy.ctl && dpkg -i multiarch-support-dummy*.deb && rm multiarch-support-dummy*.* \
    && apt-get -y purge equivs \
    && apt-get -y autoremove && apt-get clean \
    && curl -sSLf -o /etc/apt/trusted.gpg.d/microsoft.asc https://packages.microsoft.com/keys/microsoft.asc \
    && curl -sSLf -o /etc/apt/sources.list.d/mssql-release-10.list https://packages.microsoft.com/config/debian/10/prod.list \
    && apt-get -y update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18



#RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
#RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
#RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# install necessary locales
RUN apt-get update && apt-get install -y locales \
  && echo "es_ES.UTF-8" > /etc/locale.gen \
  && locale-gen

WORKDIR /app

COPY . /app/
#RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN uv sync --locked --compile-bytecode

VOLUME /app/config
VOLUME /app/application/notebooks

ARG bokeh_port=5006

ENV BOKEH_PORT=$bokeh_port

#ENTRYPOINT ["python", "./app.py"]
CMD ["uv", "run", "main.py"]
