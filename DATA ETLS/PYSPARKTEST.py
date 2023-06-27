from time import time
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('TEST').getOrCreate()
st=time()
ps=spark.read.parquet('LBR M-18.gzip',inferSchema=True,header=True)
print(str(round((time()-st),3)))
SM=spark.sparkContext.emptyRDD()
ps=ps.select(['Fiscal year/period', 'Order - Material (Key)',
       'Order - Material (Text)', 'Order', 'Operation', 'Work Center',        
       'Standard Text Key', 'Operation Text', 'End Date',
       'Operation Quantity', 'Hours Worked', 'Labor Rate', 'Labor Cost',
       'Overhead Rate', 'Overhead Cost'])
ps=ps.na.drop(how='all')
print(SM)