https://stackoverflow.com/questions/66489383/locust-script-is-getting-stuck-with-threadedconnectionpool


PG CPU Perfomance
The goal is to load Postgresql Disk and CPU, and detect a situation, when limited I/O bandwidth causes CPU usage due to I/O waits.
- see what is CPU up to at load;
0. Install Postgres on Ubuntu (use first part, without streaming replication)
https://ubuntu.com/server/docs/install-and-configure-postgresql
1.  Use a sample database (can modify than if neded)
https://wiki.postgresql.org/wiki/Sample_Databases
2.  Possible tests:
Locust Documentation: https://docs.locust.io/en/stable/index.html
Example of load test: https://miguel-codes.medium.com/unconventional-load-testing-leveraging-python-locust-for-postgresql-stress-testing-d6e07d63714b
Bulk Insert: https://github.com/burggraf/postgresql-bulk-load-tests
3. Monitor resuts:
pg_activity - to see the processes and load %: https://github.com/dalibo/pg_activity
pgcluu – to see block I/O rate:  https://pgcluu.darold.net/
also possible to use PGObserver: https://opensource.zalando.com/PGObserver/
4. See what CPU is doing under load for the postgresql processes:
https://www.site24x7.com/learn/linux/troubleshoot-high-io-wait.html
https://serverfault.com/questions/396443/diagnosing-high-cpu-waiting
The goal is to find the relation between the I/O queue length and CPU %iowait
