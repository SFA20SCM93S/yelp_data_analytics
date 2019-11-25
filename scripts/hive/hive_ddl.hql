
--Create Database called as yelp
create database yelp;

--Set current database as yelp
use yelp;

drop table yelp.business_reviews;

--Create table for storing business reviews
CREATE TABLE yelp.business_reviews
(
business_id varchar(100),
review_id varchar(100),
review_date timestamp,
useful int,
stars float,
city varchar(100),
state varchar(100),
latitude float,
longitude float,
business_name varchar(50),
postal_code varchar(5)
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

--Load the data from HDFS into the created hive table
load data inpath '/data/business_reviews/*.csv' into table yelp.business_reviews;

--select * from yelp.business_reviews limit 10;

--Create table for storing checkins by date for each business
CREATE TABLE yelp.checkins_by_date_by_business
(
business_id varchar(100),
checkin_date timestamp
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

--Load the data from HDFS into the created hive table
load data inpath '/data/checkins_by_date_by_business/part*' into table yelp.checkins_by_date_by_business;

--select * from yelp.checkins_by_date_by_business limit 10;