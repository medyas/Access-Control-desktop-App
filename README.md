# Access-Control-desktop-App 
## Access control With Raspberry Pi
### This is part of the Access-Control Project, there's also a web App using Apache2 mod_wsgi and Flask  : [Access Control Web App](https://github.com/medyas/Access-Control-Web-UI)
This app is part of my internship application, which is access control for a company.
to use the app some libraries are required such as the SPI-Py and MFRC522-Python :
```
https://github.com/lthiery/SPI-Py.git
https://github.com/mxgxw/MFRC522-python.git
```
here is a link on how to install them and setup the RFID reader : http://www.instructables.com/id/RFID-RC522-Raspberry-Pi/
also you'll need a mysql databse to connect to and get the employees info for display and save the log time for the raspberry Pi 
```
sudo apt-get install mysql-server mysql-client
sudo pip3 install mysqlclient
```
you can find tutorials on how to use mysql with python in : 
```
https://www.tutorialspoint.com/python/python_database_access.htm
or
https://www.w3schools.com/sql/default.asp
```
login to mysql using root, no password is required.
```
sudo mysql -u root -p
```
create a database
```
CREATE DATABASE wpdb;
  ```
  create a new user to access the information with it, and add permission so it can be able to only use the new created table 
 ```
CREATE USER 'wpuser'@'localhost' IDENTIFIED BY 'password_here';
GRANT ALL PRIVILEGES ON wpdb.* TO 'wpuser'@'localhost';
FLUSH PRIVILEGES;
exit
  ```
  now login with the created user
  ```
mysql -uwpuser -hlocalhost wpdb -p
  ```
you'll need to create two table 
```
CREATE TABLE `employees` (
  `id` int(8) unsigned NOT NULL AUTO_INCREMENT,
  `firstname` varchar(30) NOT NULL,
  `lastname` varchar(30) NOT NULL,
  `address` varchar(150) DEFAULT NULL,
  `card_uid` varchar(20) NOT NULL,
  `img_path` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`)
) 
```
and employee logs
```
CREATE TABLE `employee_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(8) unsigned NOT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  PRIMARY KEY (`id`),
  KEY `u_id` (`user_id`),
  CONSTRAINT `u_id` FOREIGN KEY (`user_id`) REFERENCES `employees` (`id`)
)
```

now in line 30 edit the connection to the database so it uses the new user, its password and the created table
```
db = DataBase("localhost","rfid","password","userData" )    
```

add data to the employees tables with the RFID card reference and when it's launched everything should work.

![Alt imgs](imgs/des-a.png?raw=true "Title")
