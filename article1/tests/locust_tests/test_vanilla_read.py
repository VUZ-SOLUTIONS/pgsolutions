import logging

import psycopg
from locust import User, TaskSet, task, between, events
import time

log = logging.getLogger()
log.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('locustfile.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
log.addHandler(fh)


def create_conn(conn_string):
    #log.info("Connect and Query PostgreSQL")
    conn = psycopg.connect(conn_string)
    return conn


def execute_query(conn_string, query):
    db_conn = create_conn(conn_string)
    db_query = db_conn.cursor().execute(query)
    return db_query


class PostgresClient:

    def __getattr__(self, name):
        def request_handler(*args, **kwargs):
            start_time = time.time()
            try:
                res = execute_query(*args, **kwargs)
                response_time = int((time.time() - start_time) * 1000)
                #log.info("{} Started task".format(response_time))

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
                log.error("error {}".format(e))

        return request_handler


class CustomTaskSet(TaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.conn_string = "postgresql://postgres:atmain125@localhost:54322/Adventureworks"


    log.info("Started task")

    @task(5)
    def run_query(self):
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
        self.client.execute_query(
            self.conn_string,
            sql,
        )


# This class will be executed when you run locust
class PostgresLocust(User):
    min_wait = 0
    max_wait = 1
    tasks = [CustomTaskSet]
    wait_time = between(min_wait, max_wait)

    def __init__(self, environment, *args):
        super().__init__(environment)
        self.client = PostgresClient()