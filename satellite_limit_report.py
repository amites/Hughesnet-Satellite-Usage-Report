from BeautifulSoup import BeautifulSoup
from datetime import date, datetime, timedelta
import re
import urllib2, urllib

url = 'http://customercare.myhughesnet.com/act_usage.cfm'
color = '66CCFF'
data = {
  'siteid' : False, #Enter Site Id here as 'siteid' : 'SITEID',
  'Submit' : 'Submit',
}

if not data['siteid']:
    data['siteid'] = raw_input('Enter your hughesnet site id: ')

# disabled for simple counter to pull last 24 rows
today = date.today()
yesterday_str = datetime.strftime((today - timedelta(days=1)), '%m/%d/%Y')
today_str = datetime.strftime(today, '%m/%d/%Y')

data['themonth'] = datetime.strftime(today, '%Y %m')


# set to work for central time
# TODO: update to set to current hour in EST and substract 1
last_hour = int(datetime.strftime(datetime.now(), '%H'))

#open web-site w/ POST data & return page
def readPage(url, data=False, run=True):
    if data:
        vals = urllib.urlencode(data)
        req = urllib2.Request(url, vals)
        count = 0
        while run:
            try:
                response = urllib2.urlopen(req)
                run = False
            except:
                count += 1
                print "Unable to connect - trying again - count: %s." % count
        the_page = response.read()
        return the_page
    else:
        return False

#extract number from string
def pullNadd(cell):
    str1 = str(cell)
    match = re.search(r"([0-9\.]+)", str1)
    return float(match.group(1))

# Input: row as beautifulSoup object row from table
# Output: string of date from row
def get_row_date(row):
    return str(row.findAll('td')[0].contents[0])

# Input: row as beautifulSoup object row from table
# Output: integer of beginning hour from row
def get_row_time_begin(row):
    return int(str(row.findAll('td')[1].contents[0]).split(':')[0])

the_page = readPage(url, data)
#the_page = open('report-page.html', 'r').read()

soup = BeautifulSoup(the_page)
table = soup('table')[8]

usage = 0
i = -24

print 'Total Usage\t|  Hourly Usage\t|  Time  \t |  FAP'

while i < 0:
    try:
        row = table.findAll('tr')[i]
        row_date = get_row_date(row)
        cur_usage = 0
        if row_date == today_str or (row_date == yesterday_str and get_row_time_begin(row) >= last_hour):
            #print row.prettify()
            #print "\n\n\n\n"
            if not re.search(color, str(row.findAll('td')[0])):
                # download
                #str1 = str(row.findAll('td')[4].contents[0])
                #match = re.search(r"([0-9\.]+)", str1)
                #use = float(match.group(1))
                #usage += use
                #print '%s \n' % use
                cur_usage = pullNadd(row.findAll('td')[4].contents[0])
                # upload
                #str1 = str(row.findAll('td')[6].contents[0])
                #match = re.search(r"([0-9    \.]+)", str1)
                #use = float(match.group(1))
                #usage += use
                #print '%s \n' %use
                cur_usage += pullNadd(row.findAll('td')[6].contents[0])
                usage += cur_usage
                row_time = datetime.strftime(datetime.strptime(str(row.findAll('td')[1].contents[0]), '%H:%M'), '%I:%M %p')
                fap = row.findAll('td')[5].contents[0]
                print '%s MB  \t|  %s MB  \t|  %s EST  |  %s' % (usage, cur_usage, row_time, fap)
        #else:
            #print 'FAILED: row_date: %s  - today_str: %s  - yesterday_str: %s  - row_time: %s' % (row_date, today_str, yesterday_str, get_row_time_begin(row))
    except:
        print "First of the month - updates needed to make this accurate."
    i += 1

#print usage
