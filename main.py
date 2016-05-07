#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import pyotp
import jinja2
import logging
import os
from google.appengine.api import mail

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'],
  autoescape=True)
userOtpMap = {}
otpEntered = False
def gen_otp(email):
  if not userOtpMap.has_key(email):
    userOtpMap[email] = pyotp.random_base32()
  
class MainHandler(webapp2.RequestHandler):
    def get(self):
      template = JINJA_ENVIRONMENT.get_template('index.html')
      self.response.out.write(template.render())

class OtpHandler(webapp2.RequestHandler):
  def post(self):
    email = self.request.get('email')
    gen_otp(email)
    totp = pyotp.TOTP(userOtpMap[email])
    mail.send_mail(sender="OTP <manasaalisetty@gmail.com>",
      to=email,
      subject="OTP - No-reply",
      body=str(totp.now())
      )
    template_values = {
      'email' : email,
      'entered' : otpEntered
    }
    template = JINJA_ENVIRONMENT.get_template('otp.html')
    self.response.out.write(template.render(template_values))
    # except:
    #   self.response.out.write("Status 500 Error has occured")

class ThanksHandler(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        otp = self.request.get('otp')
        otpEntered = True
        totp = pyotp.TOTP(userOtpMap[email])
        if totp.verify(otp):
          template_values = {
            'email' : email
          }
          template = JINJA_ENVIRONMENT.get_template('thank.html')
          self.response.out.write(template.render(template_values))
        else:
          template_values = {
            'email' : email,
            'otp':totp.verify(otp),
            'entered' : otpEntered
          }
          template = JINJA_ENVIRONMENT.get_template('otp.html')
          self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/verify', OtpHandler),
    ('/thanks', ThanksHandler)
], debug=True)
