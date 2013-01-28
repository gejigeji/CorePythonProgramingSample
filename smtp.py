from smtplib import SMTP as smtp

mail_host = 'smtp.qq.com'
mail_user = '654428746@qq.com'
mail_pass = '******'

to_list = ('jdxu@stu.xidian.edu.cn')
#msg['Subject'] = smtplib test
#msg['From'] = mail_user
#msg['To'] = ';'.join(to_list)
msg='''From: 654428746@qq.com\r\nTo: jdxu@stu.xidian.edu.cn\r\nSubject: smtplib test msg\r\n\r\nXXXXXX\r\n.'''

s = smtp()
s.connect(mail_host)
s.login(mail_user,mail_pass)
s.sendmail(mail_user,to_list,msg)
s.quit()
