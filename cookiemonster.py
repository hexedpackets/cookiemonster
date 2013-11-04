#!/usr/bin/env python
"""
CookieMonster Version 0.2

Licensed under MIT License (see LICENSE)
(C) William Huba 2010
"""

from random import randint


def encodedata(orig):
  encoded = ""
  for i in orig:
    val = ord(i)
    if val >= 42 and val != 127:
      encoded += str(val-32)
    elif val >= 32 and val < 42:
      encoded += "0" + str(val-32)
    elif val == 10:
      encoded += "95"

  return encoded


def decodedata(encoded):
  if len(encoded) % 2 != 0:
    raise ValueError("Encoded message must contain an even number of digits")

  i = 0
  orig = ""
  while i < len(encoded):
    if int(encoded[i:i+2]) == 95:
      orig += chr(13) + chr(10)
    else:
      orig += chr(int(encoded[i:i+2]) + 32)
    i += 2

  return orig


def buffercookie(cookie, length):
  while len(cookie) < length:
    cookie += str(randint(0, 9))
  return cookie


def createcookies(msg, cookie_id=None):
  if cookie_id is None:
    cookie_id = str(randint(10000000, 99999999))

  ## Max length for a set of cookies is 67 right now, however it needs to be even
  if len(msg) > 33:
    raise NotImplementedError("Message must be 33 characters or less")

  raw = encodedata(msg)
  cookies = {
      "utma": cookie_id,
      "utmb": cookie_id,
      "utmc": cookie_id,
      "utmz": cookie_id,
  }

  cookies['utma'] += "." + raw[:9]
  cookies['utma'] = buffercookie(cookies['utma'], 18)
  cookies['utma'] += "." + raw[9:19]
  cookies['utma'] = buffercookie(cookies['utma'], 29)
  cookies['utma'] += "." + raw[19:29]
  cookies['utma'] = buffercookie(cookies['utma'], 40)
  cookies['utma'] += "." + raw[29:39]
  cookies['utma'] = buffercookie(cookies['utma'], 51)

  ##length goes here
  cookies['utma'] += "." + str(len(raw))

  #cookies['utma'] += "." + raw[39:41]
  #cookies['utma'] = buffercookie(cookies['utma'], 54)

  cookies['utmb'] += "." + raw[39:41]
  cookies['utmb'] = buffercookie(cookies['utmb'], 11)
  cookies['utmb'] += "." + raw[41:43]
  cookies['utmb'] = buffercookie(cookies['utmb'], 14)
  cookies['utmb'] += "." + raw[43:53]
  cookies['utmb'] = buffercookie(cookies['utmb'], 25)

  cookies['utmz'] += "." + raw[53:63]
  cookies['utmz'] = buffercookie(cookies['utmz'], 19)
  cookies['utmz'] += "." + raw[63:65]
  cookies['utmz'] = buffercookie(cookies['utmz'], 22)
  cookies['utmz'] += "." + raw[65:66]
  cookies['utmz'] = buffercookie(cookies['utmz'], 24)
  cookies['utmz'] += ".utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)"

  return cookies


def processcookies(raw):
  cookies = {}

  cooklist = raw.split("; ")
  if len(cooklist) == 1:
    cooklist = raw.split(", ")

  for line in cooklist:
    temp = line.split("=")
    try:
      cookies[temp[0].lstrip("_")] = temp[1]
    except IndexError:
      pass

  utma = cookies['utma'].split(".")
  utmb = cookies['utmb'].split(".")
  utmz = cookies['utmz'].split(".")

  length = int(utma[-1])

  encoded = "".join(utma[1:5])
  encoded += "".join(utmb[1:])
  encoded += "".join(utmz[1:4])

  msg = decodedata(encoded[:length])
  return msg


def standalone_process(pkt):
  try:
    load = pkt.load.split("\n")
  except:
    return

  for header in load:
    if "Cookie:" in header:
      if "__utmc" in header:
        cookies = header[header.index(" ")+1:]
        print "\nRequest contains following cookies:"
        print cookies
        print "\nDecoded message is:"
        print processcookies(cookies)
      break


if __name__ == '__main__':
  import sys

  if len(sys.argv) == 2 and sys.argv[1] == "-s":
    ## Standalone sniffing mode
    from scapy.all import sniff

    print "Entering standalone sniffing mode"
    print "Warning! Can not send responses in this mode!"

    sniff(filter="tcp and dst port 80", prn=standalone_process)
  elif len(sys.argv) == 2 and sys.argv[1] == "-h":
    ## Usage message

    print "Client: cookiemonster.py [server] [message]"
    print "Server: cookiemonster.py -s"
  elif len(sys.argv) == 3:
    ## Client mode
    import urllib2

    print "Sending message to " + sys.argv[1] + "..."

    l = 0
    while l < len(sys.argv[2]):
      orig = sys.argv[2][l:l+33]
      l += 33
      cookieDict = createcookies(orig)
      cookie = ""
      for c in cookieDict.keys():
        cookie += "__" + c + "=" + cookieDict[c] + "; "
      cookie.rstrip('; ')

      request = urllib2.Request('http://'+sys.argv[1])
      request.add_header('Cookie', cookie)
      request.add_header('User-Agent', "Covert channel client!")

      serverpage = urllib2.urlopen(request)

      print "Message sent!"
      print

      try:
        print processcookies(serverpage.info()['Set-Cookie'])
      except KeyError:
        print "No cookies in response"

      #print serverpage.read()

  else:
    ## CGI Script
    import Cookie
    import os
    import time

    cookies = Cookie.Cookie()
    setcooks = Cookie.Cookie()

    try:
      cookies.load(os.environ["HTTP_COOKIE"])
    except KeyError:
      pass

    print "Content-Type: text/html"

    if '__utmc' in cookies:
      ## Look at message from client
      cstring = "; ".join([c + "=" + cookies[c].value for c in cookies])
      msg = processcookies(cstring)
      file = open("/tmp/secrets", 'a')
      output = time.strftime("%H:%M:%S %m-%d-%y") + "\t" + msg + "\n"
      file.write(output)
      file.close()

      ## Generate message from server
      try:
        file = open("/tmp/responses")
        response = createcookies(file.read())
        file.close()
        for c in response.keys():
          setcooks[c] = response[c]
      except IOError:
        setcooks = cookies

      print setcooks
    else:
      msg = "Nothing to see here. Move along."

    print
    print "<html><head><title>SECRET COVERT CHANNEL SSHHH DONT TELL ANYONE</title></head><body>"
    print msg
    print "<br>"
    print "</body></html>"
