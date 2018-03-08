#Automated SD County Emergency email

#Imports
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from secrets import EMAIL_FROM, EMAIL_TO, EMAIL_PASS, EMAIL_SERVER, DBPATH
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import sqlite3

#Set up the database
callsdb_file = DBPATH + "sdcedb.sqlite"
db = sqlite3.connect(callsdb_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS calls (dbid INTEGER PRIMARY KEY, dbdate TEXT, dbtitle TEXT, dblink TEXT, dbupdatetime timestamp)')
db.commit()

def storeCall():
        c.execute('SELECT dbid FROM calls WHERE dbdate=?', (date,)) #search for the call in the DB by dispatch date/time
        thisCall = c.fetchone()
        now = datetime.now()
        if thisCall > 0:  #if call exists in DB
                print "# " + date + "  |  " + title
                return 0
        else:  #if this call is new
                c.execute('INSERT INTO calls(dbdate, dbtitle, dblink, dbupdatetime) VALUES(?,?,?,?)', (date, title, link, now))
                db.commit()
                c.execute('SELECT * FROM calls WHERE dbdate=?', (date,))
                call = c.fetchone()
                print "+" + str(call)
                return 1
        return -1


def sendEmail(footer):
        fromaddr = EMAIL_FROM
        toaddr = EMAIL_TO
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject']= "SDCE: " + calltype
        body = link + "\n Published: " + date
        msg.attach(MIMEText(body, 'plain'))
        email = smtplib.SMTP(EMAIL_SERVER, 587)
        email.ehlo()
        email.starttls()
        email.ehlo()
        email.login(EMAIL_FROM,EMAIL_PASS)
        text = msg.as_string()
        email.sendmail(EMAIL_FROM, EMAIL_TO, text)
        email.quit()
        print "Emailed: " + calltype + " @ " + calldate
        return


###Main:
r = requests.get('http://www.sdcountyemergency.com/updates')
soup = BeautifulSoup(r.text, 'html.parser')

table = soup.find("table", { "class" : "table table-striped news-list" })
for row in table.findAll("tr"):
        cells = row.findAll("td")
        if str(cells[1].get_text()).strip() == "Headline":
                print "Table found! Processing... \n"
        elif len(cells) == 3:
                date = str(cells[0].get_text()).strip()
                title = str(cells[1].get_text()).strip()
                link = "http://www.sdcountyemergency.com" + str(cells[1].find("a")["href"]).strip()
##              print date + "  |  " + title
                savetype = storeCall() #Return type is 0 for old, 1 for new
##              print savetype
#               if savetype > 0
#                       sendEmail()
#               if savetype < 0
#                       title = "Error!"
#                       sendEmail()

print "\nFinished."
exit()
