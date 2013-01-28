from poplib import POP3

p = POP3('stumail.xidian.edu.cn')
p.user('jdxu@stu.xidian.edu.cn')
p.pass_('******')
x=p.stat()
rsp, msg, siz = p.retr(x[0])
for eachLine in msg:
    print eachLine
