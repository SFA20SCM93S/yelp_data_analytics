#!/usr/bin/env python
# coding: utf-8

# In[12]:


# Import libraries required to find pyspark installations on jupyter notebook
import findspark
findspark.init()
findspark.find()
import pyspark

# Import the required pyspark libraries that will help us explode the list of checkin dates for each business 
# into individual rows 
from pyspark.sql.functions import col, split
from pyspark.sql.functions import explode


# In[2]:


# Import SparkSession from Pyspark
from pyspark.sql import SparkSession

# Create spark object with the necessary configuration
spark = SparkSession.builder .appName('EDA') .master('local') .enableHiveSupport() .getOrCreate()


# In[6]:


# Read all the input files (stored on HDFS in JSON format) and create a spark dataframe on top of it
review = spark.read.json('hdfs://0.0.0.0:19000/data/review.json')


# In[7]:


business = spark.read.json('hdfs://0.0.0.0:19000/data/business.json')
checkin = spark.read.json('hdfs://0.0.0.0:19000/data/checkin.json')


# In[22]:


# create a temporary view on top of each dataframe for querying using Spark SQL
review.createOrReplaceTempView("review")
business.createOrReplaceTempView("business")
checkin.createOrReplaceTempView("checkin")


# In[40]:


# Since there are thousands of categories, we will focus our analysis only on categories such as restaurant, pizza & sandwich.
business_subset = spark.sql("select b.*, row_number() over(partition by b.state order by b.review_count desc) as rnk from business b where (lower(categories) like '%restaurant%' or lower(categories) like '%pizza%' or lower(categories) like '%sandwich%')")

business_subset.createOrReplaceTempView("business_subset")


# In[53]:


# Join reviews with subset of businesses to get it's required details.
business_reviews=spark.sql("select r.business_id, r.review_id, r.date, r.useful, r.stars, b.city, b.state, b.latitude, b.longitude, b.name, b.postal_code from review r inner join (select * from business_subset b where rnk<=50) b on r.business_id=b.business_id")


# In[44]:


# Split the string column on the basis of comma to create a list of dates
checkin_date_list=checkin.select(col("business_id"), split(col("date"), ",\s*").alias("date"))

# Converting the array of dates into individual rows
checkin_explode=checkin_date_list.withColumn("date", explode(checkin_date_list.date))

# Create a temporary view for querying data in Spark SQL
checkin_explode.createOrReplaceTempView("checkin_explode")

# Filter data for subset of categories and locations as we did in above steps
checkin_explode_subset=spark.sql("select c.business_id, c.date from checkin_explode c inner join (select * from business_subset b where rnk<=50) b on c.business_id=b.business_id")


# In[56]:


# Write spark datframe to HDFS
checkin_explode_subset.write.csv('/data/checkins_by_date_by_business')
business_reviews.write.csv('/data/business_reviews')


# In[62]:


reviews_bad_review=spark.sql("select r.text from review r where business_id='DkYS3arLOhA8si5uUEmHOw' and stars=1 order by useful desc limit 100")

reviews_good_review=spark.sql("select r.text from review r where business_id='DkYS3arLOhA8si5uUEmHOw' and stars=5 order by useful desc limit 100")


# In[67]:


reviews_bad_review_pd=reviews_bad_review.toPandas()
reviews_good_review_pd=reviews_good_review.toPandas()

# Let's make some word clouds!
# Terminal / Anaconda Prompt: conda install -c conda-forge wordcloud
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction import text 

stop_words = text.ENGLISH_STOP_WORDS.union(['good','went','did','didn''t','said','it','pizza','slice','told','order','ordered','food','just','I''m','going','like','really','asked','place','time','got','called','came'])

wc = WordCloud(stopwords=stop_words, background_color="white", colormap="Dark2",
               max_font_size=150, random_state=42)

import json
import csv
import re
import string
import pandas as pd

def clean_text(text):
    '''Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.'''
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    '''Get rid of some additional punctuation and non-sensical text that was missed the first time around.'''
    text = re.sub('[‘’“”…]', '', text)
    text = re.sub('\n', '', text)
    return text

reviews_bad_review_pd['text'] = reviews_bad_review_pd['text'].apply(lambda x: clean_text(x))
reviews_good_review_pd['text'] = reviews_good_review_pd['text'].apply(lambda x: clean_text(x))

wc.generate(' '.join(reviews_bad_review_pd['text']))
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()
plt.savefig("C:\\bigdata\sshrung14\yelp_data_analytics\docs\\bad_reviews_word_cloud2.png")

wc.generate(' '.join(reviews_good_review_pd['text']))
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()
plt.savefig("C:\\bigdata\sshrung14\yelp_data_analytics\docs\\good_reviews_word_cloud2.png")


# In[ ]:




