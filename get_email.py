#!/usr/bin/env python3
# -*- coding: utf8 -*-
'''
From: http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb49318210
      3fac9270762a000/001408244819215430d726128bf4fa78afe2890bec57736000
'''

import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr


def main():
    M = poplib.POP3('pop.exmail.qq.com', 110)
    M.user(r'stephensun@shunshunliuxue.com')
    M.pass_('Asdf1234')
    resp, mails, octets = M.list()
    print('resp: {}'.format(resp))
    print('mails: {}'.format(mails))
    print('octets: {}'.format(octets))

    count = len(mails)
    resp, lines, octets = M.retr(count)
    print('lines: {}'.format(lines))
    msg_content = '\r\n'.join(line.decode('utf8') for line in lines)
    msg = Parser().parsestr(msg_content)
    M.quit()

    print_info(msg)


def print_info(msg, indent=0):
    if indent == 0:
        # 邮件的From, To, Subject存在于根对象上:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    # 需要解码Subject字符串:
                    value = decode_str(value)
                else:
                    # 需要解码Email地址:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        # 如果邮件对象是一个MIMEMultipart,
        # get_payload()返回list，包含所有的子对象:
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % ('  ' * indent, n))
            print('%s--------------------' % ('  ' * indent))
            # 递归打印每一个子对象:
            print_info(part, indent + 1)
    else:
        # 邮件对象不是一个MIMEMultipart,
        # 就根据content_type判断:
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            # 纯文本或HTML内容:
            content = msg.get_payload(decode=True)
            # 要检测文本编码:
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % ('  ' * indent, content + '...'))
        else:
            # 不是文本,作为附件处理:
            print('%sAttachment: %s' % ('  ' * indent, content_type))


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
        return(value)


def guess_charset(msg):
    # 先从msg对象获取编码:
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，再从Content-Type字段获取:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
            return charset

if __name__ == '__main__':
    main()
