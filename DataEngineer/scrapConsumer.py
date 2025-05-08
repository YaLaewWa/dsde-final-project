#!/opt/anaconda3/envs/dsde-cp/bin/python
import asyncio
from kafka import KafkaConsumer
import avro.schema
import avro.io
import io
import pandas as pd
from dateutil import parser
import joblib
from model.severity import Judge


scrapingData_file = 'avro/scrapingData.avsc'
modelFile = 'model/xgboost_model_pipeline.pkl'
scrapeSchema = avro.schema.parse(open(scrapingData_file).read())
pipeline = joblib.load(modelFile)
kafka_broker = 'localhost:9092'
severityMode = Judge()

consumer = KafkaConsumer(
  'scrapingData',
    bootstrap_servers=[kafka_broker],
    enable_auto_commit=True,
    value_deserializer=lambda x: deserialize(scrapeSchema, x))

def deserialize(schema, raw_bytes):
  bytes_reader = io.BytesIO(raw_bytes)
  decoder = avro.io.BinaryDecoder(bytes_reader)
  reader = avro.io.DatumReader(schema)
  return reader.read(decoder)

def serialize(schema, obj):
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    writer = avro.io.DatumWriter(schema)
    writer.write(obj, encoder)
    return bytes_writer.getvalue()

def predictTTS(o):
  tmp = {'timestamp' : [parser.parse(o['timestamp'])], 'subdistrict' : [o['subdistrict']], 'comment' : [o['comment']], 'organization' : [o['organization']]}
  X = pd.DataFrame(data = tmp)
  X['day_of_week'] = X['timestamp'].dt.dayofweek
  X['is_weekend'] = X['day_of_week'].apply(lambda x: 1 if x in [5, 6] else 0)
  X['hour_of_day'] = X['timestamp'].dt.hour
  X['is_night'] = X['hour_of_day'].apply(lambda x: 1 if (x < 6 or x >= 20) else 0)
  X = X.drop(columns='timestamp')
  return pipeline.predict(X)

def predictSeverity(o):
  return asyncio.run(severityMode.getAnswer(o['comment'])).strip("\n")

def scrapConsumer(filename):
  firstTime = True
  try:
    df = pd.read_csv(filename, index_col=0)
    if (df.shape[0] > 0):
      firstTime = False
  except:
    print("No file found")

  print('Running Consumer with AVRO')
  for message in consumer:
    tts = predictTTS(message.value)
    severity = predictSeverity(message.value)
    tmp = {k : [v] for k,v in message.value.items()}
    tmp['time_to_solve'] = tts
    tmp['severity'] = [severity]

    if (firstTime):
      df = pd.DataFrame(data = tmp)
      df.to_csv(filename)
      firstTime = False
    else:
      df = pd.concat([df, pd.DataFrame(data = tmp)], ignore_index=True, axis = 0)
      df.to_csv(filename)


scrapConsumer("data.csv")
  
