import logging

#import psycopg
import psycopg2
import psycopg2
from psycopg2 import pool


from locust import User, TaskSet, task, between, events
import time


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s] - [%(filename)s:%(lineno)s] - [%(threadName)s] - [%(name)s] - [%(levelname)s] - %(message)s')

fh = logging.FileHandler('locustfile.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

pool = psycopg2.pool.SimpleConnectionPool(1, 20, user="postgres",
                                          password="atmain125",
                                          host="127.0.0.1",
                                          port="54322",
                                          database="Adventureworks")

def create_conn():
    conn = pool.getconn()
    return conn


def execute_query(query):
    db_conn = create_conn()
    try:
        db_query = db_conn.cursor().execute(query)
    finally:
        pool.putconn(db_conn)
    return db_query


class PostgresClient:

    def __getattr__(self, name):
        def request_handler(*args, **kwargs):
            start_time = time.time()
            try:
                res = execute_query(*args, **kwargs)
                response_time = int((time.time() - start_time) * 1000)
                logger.debug("Query result: {}".format(res))

                events.request.fire(
                    request_type="postgres",
                    name=name,
                    response_time=response_time,
                    response_length=0,
                )
            except Exception as e:
                response_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="postgres",
                    name=name,
                    response_time=response_time,
                    response_length=0,
                    exception=e,
                )
                logger.error("error {}".format(e))

        return request_handler


class CustomTaskSet(TaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        logger.info("Started task")

    @task
    def run_query(self):
        # just get the latest employee positiion
        # enddate must be null
        sql = """
        select distinct on (a.nationalidnumber) a.nationalidnumber, dep_name as last_dep_name, a.firstname, a.lastname, a.modifieddate, a.startdate, a.enddate
         from     
        (SELECT e.nationalidnumber, p.firstname, p.lastname, h.modifieddate, h.startdate, h.enddate, d.name as "dep_name", d.groupname FROM humanresources.employee e 
        left  join person.person p on p.businessentityid = e.businessentityid 
        left join humanresources.employeedepartmenthistory h on h.businessentityid = e.businessentityid 
        left join humanresources.department d on h.departmentid = d.departmentid 
        ) a 
        order by a.nationalidnumber, a.startdate desc
"""
        self.client.execute_query(sql)


# This class will be executed when you run locust
class PostgresLocust(User):
    min_wait = 0
    max_wait = 1
    tasks = [CustomTaskSet]
    wait_time = between(min_wait, max_wait)

    def __init__(self, environment, *args):
        super().__init__(environment)
        self.client = PostgresClient()