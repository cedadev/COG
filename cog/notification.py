from email.mime.text import MIMEText
import smtplib
from threading import Thread
from django.conf import settings
from cog.site_manager import siteManager

class EmailConfig:
    '''
    Class that stores the email server connection properties from a local configuration file.
    Site specific values are read from the cog_settings.cfg file through the SiteManager class.
    '''
    
    def __init__(self):
        
        self.init = False
        
        if siteManager.hasConfig(settings.SECTION_EMAIL):
            self.server = siteManager.get('email.server', section=settings.SECTION_EMAIL)
            if self.server is not None and self.server.strip() != '':
                self.port = siteManager.get('email.port', section=settings.SECTION_EMAIL)
                self.sender = siteManager.get('email.sender', section=settings.SECTION_EMAIL)
                self.username = siteManager.get('email.username', section=settings.SECTION_EMAIL)
                self.password = siteManager.get('email.password', section=settings.SECTION_EMAIL)
                self.security = siteManager.get('email.security', section=settings.SECTION_EMAIL)
                print 'Using email server=%s' %  self.server
                print 'Using email port=%s' %  self.port
                print 'Using email sender=%s' %  self.sender
                print 'Using email username=%s' %  self.username
                print 'Using email password=%s' %  self.password
                print 'Using email security=%s' %  self.security
                self.init = True
            
        if not self.init:
            print "Email configuration not found, email notification disabled"
            

# module scope email configuration
emailConfig = EmailConfig()

def notify(toUser, subject, message):
    
    # send email in separate thread, do not wait
    emailThread = EmailThread(toUser.email, subject, message)
    emailThread.start()

def sendEmail(fromAddress, toAddress, subject, message):
    
    # send email in separate thread, do not wait
    emailThread = EmailThread(toAddress, subject, message, fromAddress=fromAddress)
    emailThread.start()

        
class EmailThread(Thread):
    '''Class that sends an email in a separate thread.'''
    
    def __init__ (self, toAddress, subject, message, fromAddress=None):
        Thread.__init__(self)
        self.toAddress = toAddress
        self.subject = subject
        self.message = message
        if fromAddress is not None:
            self.fromAddress = fromAddress
        elif emailConfig.init == True:
            self.fromAddress = emailConfig.sender
        else:
            self.fromAddress = None
        
    def run(self):
        
        #print "From: %s" % self.fromAddress
        print "To: %s" % self.toAddress
        print "Subject: %s" % self.subject
        print "Message: %s" % self.message
        
        # use local mail server
        #toUser.email_user(subject, message, from_email=fromAddress)
        
        # use email relay server
        if emailConfig.init == True:
    
            # use email relay server
            msg = MIMEText(self.message)
            msg['Subject'] = self.subject
            msg['From'] = self.fromAddress
            msg['To'] = self.toAddress    
            if emailConfig.port is not None:
                s = smtplib.SMTP( emailConfig.server, emailConfig.port )
            else:
                s = smtplib.SMTP( emailConfig.server )
            if emailConfig.security=='STARTTLS':
                s.starttls()
            if emailConfig.username and emailConfig.password:
                s.login(emailConfig.username, emailConfig.password )
            s.sendmail(emailConfig.sender, [self.toAddress], msg.as_string())
            s.quit()
            print 'Email sent.'
