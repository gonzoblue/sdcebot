
#Automated SD County Emergency email

#Imports
import smtplib
import unicodedata
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

def getLinkInfo():
        linkpage = requests.get(link)
        soup = BeautifulSoup(linkpage.text, 'html.parser')
        fullInfo = soup.find('div', {'class': 'page-copy'})
        info = fullInfo.findAll('div', {'class': 'xrm-attribute-value'})
        infoText = info[2].text.strip()
        return infoText.encode('ascii', 'ignore')


def storeCall():
        c.execute('SELECT dbid FROM calls WHERE dbdate=?', (date,)) #search for the call in the DB by dispatch date/time
        thisCall = c.fetchone()
        now = datetime.now()
        if thisCall > 0:  #if call exists in DB
                print "- " + date + "  |  " + title
                return 0
        else:  #if this call is new
                c.execute('INSERT INTO calls(dbdate, dbtitle, dblink, dbupdatetime) VALUES(?,?,?,?)', (date, title, link, now))
                db.commit()
                c.execute('SELECT * FROM calls WHERE dbdate=?', (date,))
                call = c.fetchone()
                print str(call)
                return 1
        return -1


def sendEmail():
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = ','.join(EMAIL_TO)
        msg['Subject']= "[SDCE] " + title
        body = "Published: " + date + "\nTitle: " + title + "\nLink: " + link + "\n\n" + linkInfo
        msg.attach(MIMEText(body, 'plain'))
        email = smtplib.SMTP(EMAIL_SERVER, 587)
        email.ehlo()
        email.starttls()
        email.ehlo()
        email.login(EMAIL_FROM,EMAIL_PASS)
        email.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        email.quit()
        print "Emailed:\n" + body
        return


###Main:
r = requests.get('http://www.sdcountyemergency.com/updates')
soup = BeautifulSoup(r.text, 'html.parser')

table = soup.find("table", { "class" : "table table-striped news-list" })
for row in table.findAll("tr"):
        linkInfo = "-=-"
        cells = row.findAll("td")

        if len(cells) != 3:
                print "Table not correct size. Exiting."
                exit(1)

        if cells[1].get_text().strip() == "Headline":
                print "Table found! Processing... \n"
        else:
                date = cells[0].get_text().strip()
                title = cells[1].get_text().strip()
                title = unicodedata.normalize('NFKD', title).encode('ascii','ignore')
                link = "http://www.sdcountyemergency.com" + cells[1].find("a")["href"].strip()
                savetype = storeCall() #Return type is 0 for old, 1 for new
                if savetype > 0:
                        linkInfo = getLinkInfo()
                        sendEmail()
                elif savetype < 0:
                        title = "Error!"
                        sendEmail()

print "\nFinished."
exit()
