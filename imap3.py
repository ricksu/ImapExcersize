#coding=utf-8

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

def display_structure(structure, parentparts=[]):
	""" message structure"""
	print "in :", parentparts
	if parentparts: 
		name = '.'.join(parentparts) 
	else: 
		print 'HEADER' 
		name = 'TEXT'
	# Print this part's designation and its MIME type. 
	is_multipart = isinstance(structure[0], list) 
	if is_multipart: 
		print "multipart =="
		parttype = 'multipart/%s' % structure[1].lower() 
	else: 
		print "non_multipart =="
		parttype = ('%s/%s' % structure[:2]).lower() 
	print 'pos0 %-9s' % name, parttype, 
	# For a multipart part, print all of its subordinate parts; for 
	# other parts, print their disposition (if available). 
	if is_multipart: 
		print 
		subparts = structure[0] 
		for i in range(len(subparts)): 
			display_structure(subparts[i], parentparts + [ str(i + 1) ])
	else: 
		print 'structure=', structure
		if structure[6]: 
			print 'struct6 :size=%s' % structure[6], 
		if structure[8]: 
			disposition, namevalues = structure[8]
			print disposition, 
			for i in range(0, len(namevalues), 2): 
				print 'struct8 %s=%r' % namevalues[i:i+2] 

def explore_message(c, uid):
	"""explore message"""
	msgdict = c.fetch(uid, ['BODYSTRUCTURE', 'FLAGS'])

	while True:
		print 'flags:',
		flaglist = msgdict[uid]['FLAGS']
		if flaglist:
			print ' '.join(flaglist)
		else:
			print 'none flags'
		display_structure(msgdict[uid]['BODYSTRUCTURE'])
		print "---"*3
		reply = raw_input('Message %s - type a part name, or "q" :' % uid).strip()
		if reply.lower().startswith('q'):
		    break
		key = 'BODY[%s]' % reply
		try:
		    msgdict2 = c.fetch(uid, [key])
		except c._imap.error:
		    print 'error - cannot fetch section %r' % reply
		else:
			content = msgdict2[uid][key]
			if content:
				print banner
				print content.strip()
				print banner
			else:
				print 'No such section'	

def explore_folder(c, folder):
	""" list folder content"""

	c.select_folder(folder, readonly = True)
	msgdict = c.fetch("1:200", ['BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]', 'FLAGS', 'INTERNALDATE', 'RFC822.SIZE'])
	while True:
		for uid in sorted(msgdict):
			items = msgdict[uid]
			print '%6d %20s %6d bytes %s' % (
				uid, items['INTERNALDATE'], items['RFC822.SIZE'], 
				' '.join(items['FLAGS'])) 
			for i in items['BODY[HEADER.FIELDS (FROM SUBJECT)]'].splitlines(): 
				print ' ' * 6, i.strip()

		reply = raw_input('input a uid or "q" to quit\n').strip()
		if (reply.lower().startswith('q')):
			break
		try: 
		    reply = int(reply) 
		except ValueError: 
		    print 'Please type an integer or "q" to quit' 
		else: 
		    if reply in msgdict: 
		    	explore_message(c, reply) 
		    	break
	c.close_folder() 

def explore_account(c):
	"""explore the account, list the folders"""
	print 'explore account:', c
	while True:
		folderflags = {}
		data = c.list_folders()
		for flags, delimiter, name in data:
			folderflags[name] = flags
		for name in sorted(folderflags.keys()):
			print '%-30s %s' % (name, ' '.join(folderflags[name]))
		reply = raw_input('Type a folder name or "q" to quit\n').strip()
		if reply.lower().startswith('q'):
			break
		if reply in folderflags.keys():
			explore_folder(c, reply)
			break
		else:
			print 'Error: no folder ', repr(reply)
			print folderflags.keys()


if __name__ == '__main__': 
	explore_account(c)
	print 'OK ========='