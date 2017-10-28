FROM python:2.7
RUN pip install --upgrade pip
RUN pip install requests[security]
RUN pip install locustio
RUN pip list
ENV PYTHONPATH $PYTHONPATH:/
ADD ./locust_lib /locust_lib
ADD ./tests /tests

ADD run.sh /usr/local/bin/run.sh
RUN chmod 755 /usr/local/bin/run.sh

EXPOSE 8089 5557 5558

CMD ["/usr/local/bin/run.sh"]
