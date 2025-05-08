#!/opt/anaconda3/envs/dsde-cp/bin/python
from producer.seleniumTraffy import scrape
import time

while True:
  scrape("data.csv")
  time.sleep(60)
  break;