service mysql restart
mysql --user="root" --password="" < config.sql
mysql --user="root" --password="" < test.sql
mysql --user="root" --password="" 'user_rides' < data.sql