#Ingest the data to HDFS
sh ingest_into_hdfs.sh

if [ $? -eq 0 ]
then
echo "Data imported to HDFS"
else
echo "Import to HDFS failed"
exit 1
fi

#Executing pig script for exploding checkins data into individual rows
pig -x mapreduce process_checkins_dataset.pig

if [ $? -eq 0 ]
then
echo "Checkins data transformation completed"
else
echo "Checkins data transformation failed"
exit 1
fi


#Execute the pyspark script to transform the reviews and business data
pyspark data_preprocessing_and_transformations.py

if [ $? -eq 0 ]
then
echo "business and reviews data transformation completed"
else
echo "business and reviews data transformation failed"
exit 1
fi

#Execute hive scripts to load the tranformed data from hdfs to a hive table
hive -f hive_ddl.hql

if [ $? -eq 0 ]
then
echo "business, reviews and checkins data loaded to hive"
else
echo "failed to load business, reviews and checkins data to hive"
exit 1
fi
