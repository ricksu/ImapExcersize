import getpass, sys
from imapclient import IMAPClient

hostname = "imap.aliyun.com"
username = "ricksucn@aliyun.com"
banner = "=" * 72

c = IMAPClient(hostname, ssl = True) 
try:
	c.login(username, getpass.getpass())
except c.Error, e:
	print 'could not login:', e
	sys.exit(1)
def delete_check(c, uid):
	reply = raw_input('Delete this message ' + str(uid) + " ?\n").strip()
	if (reply == "y"):
	    c.delete_messages([uid]) 
    	c.expunge() 

def get_msg_ids(c, folder):
	c.select_folder(folder, readonly = True)
	msgdict = c.fetch("200:300", ['BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)]', 'FLAGS', 'INTERNALDATE', 'RFC822.SIZE'])
	print 'message size:%d\n'% len(msgdict)

	for uid in sorted(msgdict):
		items = msgdict[uid]
		print '%6d %20s %6d bytes %s' % (
			uid, items['INTERNALDATE'], items['RFC822.SIZE'], 
			' '.join(items['FLAGS'])) 
		for i in items['BODY[HEADER.FIELDS (FROM TO SUBJECT DATE)]'].splitlines(): 
			print ' ' * 6, i.strip()
		delete_check(c, uid)

	c.close_folder()

if __name__ == '__main__': 
	get_msg_ids(c, "Inbox")