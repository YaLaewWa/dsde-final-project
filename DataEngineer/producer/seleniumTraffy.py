#external import 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from kafka import KafkaProducer
import avro.schema
import avro.io
import io
import time

#internal import 
from producer.miscFunction import coordinateParser, parseDate, writeCheckpointFile, readCheckpointFile

try:
  schema_file = 'avro/scrapingData.avsc'
  schema = avro.schema.parse(open(schema_file).read())
  kafka_broker = 'localhost:9092'
  producer = KafkaProducer(bootstrap_servers=[kafka_broker])
except:
  print("Kafka Broke")

def serialize(schema, obj):
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    writer = avro.io.DatumWriter(schema)
    writer.write(obj, encoder)
    return bytes_writer.getvalue()

def sendToKafka(t_id, t, org, comment, coord, subdistrict, ts, photo):
  o = {"ticket_id" : t_id,
  "type" : t,
  "organization" : org,
  "comment" : comment,
  "coords" : coord,
  "subdistrict" : subdistrict,
  "timestamp" : ts,
  "photo" : photo
  }
  producer.send('scrapingData', serialize(schema, o))

path = "https://fondue.traffy.in.th/bangkok"
secPath = "https://fondue.traffy.in.th/?page=detail&ticketID="
checkpointFilename = "checkpoint.txt"

def scrape(filename):
  driver = webdriver.Firefox()
  

  def scrollDown(elem):
    for _ in range(10):
      time.sleep(.01)
      elem.send_keys(Keys.PAGE_DOWN)

  ticketID = []
  tag = []
  description = []
  timestamp = []
  coors = []
  subdistrict = []
  organization = []
  imagesUrl = []
  index = 0

  try:
    driver.get(path)
    driver.implicitly_wait(10)

    latestTicket = readCheckpointFile(checkpointFilename)
    elem = driver.find_element(By.TAG_NAME, "body")
    endJobFlag = False

    while (index < 12 and not endJobFlag):
      roots = driver.find_elements(By.CLASS_NAME, "containerData")
      for i in range(index, len(roots)):
        root = roots[i]
        ticket = root.find_element(By.CLASS_NAME, "ticket_id").text
        print(ticket)

        #If ticket exist exit program
        if (ticket == latestTicket):
          print(ticket)
          print("My job is done, me go home")
          endJobFlag = True
          break
        
        status = root.find_element(By.CLASS_NAME, "title-state").text
        if ("เสร็จสิ้น" in status):
          continue

        ticketID.append(ticket)
        tmp = root.find_elements(By.CLASS_NAME,"tags-problemType")
        tagSet = []
        for t in tmp:
          tagSet.append(t.find_element(By.TAG_NAME, 'p').text)
        tag.append('{'+str(tagSet).strip("'[]")+'}')
        tmp = root.find_element(By.CLASS_NAME, 'description')
        tmp = tmp.find_elements(By.TAG_NAME, 'span')
        timestamp.append(parseDate(root.find_elements(By.CLASS_NAME, 'detailTimes')[1].text))
        imagesUrl.append(root.find_element(By.CLASS_NAME, 'img_post').get_attribute('src'))
        tmp = root.find_elements(By.CLASS_NAME, 'div_row_txt')[1]
        subdistrict.append((tmp.find_element(By.TAG_NAME, 'p').text).split(' ')[-1])
        tmp = root.find_elements(By.CLASS_NAME, 'detailReportPost')[-1]
        organization.append(tmp.find_elements(By.TAG_NAME, 'span')[-1].text)
        driver.switch_to.new_window('tab')
        driver.get(secPath+ticketID[-1])
        wait = WebDriverWait(driver, 10)
        cord = wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        coors.append(coordinateParser(driver.find_element(By.XPATH, '//a[@rel="noopener"]').get_attribute('href')))
        description.append(driver.find_element(By.CLASS_NAME, 'txt-comment').text)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        # t_id, t, org, comment, coord, subdistrict, ts, photo
        sendToKafka(ticketID[-1], tag[-1], organization[-1], description[-1], coors[-1], subdistrict[-1], timestamp[-1], imagesUrl[-1])
        print("Done")

      #After exit each loop
      index = len(roots)
      scrollDown(elem)

  finally:
    writeCheckpointFile(driver.find_element(By.CLASS_NAME, "containerData").find_element(By.CLASS_NAME, "ticket_id").text, checkpointFilename)
    driver.close()
    driver.quit()