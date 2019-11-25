checkin = LOAD '/data/checkin.json' USING JsonLoader('business_id:chararray, date:chararray');

-- split by ',' and create a row so we can dereference it later
splt = foreach checkin generate business_id, FLATTEN(STRSPLIT(date, '\\,')) ;

-- first column is business_id, rest is converted into a bag and flatten it to make rows
id_vals = foreach splt generate $0 as business_id, FLATTEN(TOBAG(*)) as value;

-- there will be records with (business_id, business_id), but id should not have ':'
id_vals = foreach id_vals generate business_id, INDEXOF(value, ':') as p, STRSPLIT(value, ':', 2) as vals;
final = foreach (filter id_vals by p != -1) generate business_id, FLATTEN(vals) as (col, val);

-- Write final output to csv
store final into '/data/checkins_by_date_by_business_pig' using PigStorage(',');