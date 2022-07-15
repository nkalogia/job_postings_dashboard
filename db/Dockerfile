FROM postgres

RUN mkdir status
RUN chown -R postgres /status
COPY initdb.d /docker-entrypoint-initdb.d
RUN sed -i 's/\r$//' /docker-entrypoint-initdb.d/*.sh