from datetime import timedelta, timezone, datetime
def coordinateParser(url):
  a = url[32:50].split("&")
  x, y = a[0].split(',')
  return y + ',' + x

def parseDate(date):
  monthParse = {
    'ม.ค.': 1,
    'ก.พ.': 2,
    'มี.ค.': 3,
    'เม.ย.': 4,
    'พ.ค.': 5,
    'มิ.ย.': 6,
    'ก.ค.': 7,
    'ส.ค.': 8,
    'ก.ย.': 9,
    'ต.ค.': 10,
    'พ.ย.': 11,
    'ธ.ค.': 12,
  }
  dd, mm, yy, time, _ = date.split()
  hh, mi = time.split(':')
  timeString = datetime(int('25'+yy)-543, monthParse[mm], int(dd), int(hh), int(mi), 0, 0, timezone(timedelta(hours=7))).astimezone(timezone.utc)
  return timeString.isoformat()

def writeCheckpointFile(ticket_id, filename):
  file = open(filename, 'w')
  file.write(ticket_id)
  file.close()

def readCheckpointFile(filename):
  try:
    file = open(filename, 'r')
    ticket_id = file.readline()
    file.close()
    return ticket_id
  except:
    return ""