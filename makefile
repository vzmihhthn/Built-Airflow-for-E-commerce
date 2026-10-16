to_mysql:
	docker exec -it de_mysql -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" ${MYSQL_DATABASE}
to_mysql_root:
	docker exec -it de_mysql mysql -u"root" -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASE}

# nhớ bật local_infile - on : SET GLOBAL local_infile = 1;
mysql_create:
	docker exec -it de_mysql mysql --local_infile -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" ${MYSQL_DATABASE} -e"source /tmp/load_dataset/mysql_datasource.sql" 
mysql_load:
	docker exec -it de_mysql mysql --local_infile -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" ${MYSQL_DATABASE} -e"source /tmp/load_dataset/mysql_load.sql"


# docker exec -it mysql mysql -u"root" -p"admin"  olist
# docker exec -it mysql mysql -uadmin -padmin -e "DROP DATABASE olist; CREATE DATABASE olist;"
# docker exec -it mysql mysql -uadmin -padmin olist -e "source /tmp/load_dataset/olist.sql"
# docker exec -it mysql mysql --local_infile=1 -uadmin -padmin olist -e "source /tmp/load_dataset/load_data.sql"