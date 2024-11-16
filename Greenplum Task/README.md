```commandline
docker pull andruche/greenplum:7
docker run --name greenplum -p 5432:5432 -d andruche/greenplum:7
psql -U gpadmin -d postgres
```