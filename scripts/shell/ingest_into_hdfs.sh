# create directory to store the input files
hadoop fs -mkdir /data

# Import input files in HDFS
hadoop fs -put review.json /data
hadoop fs -put business.json /data
hadoop fs -put checkin.json /data