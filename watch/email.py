from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import notifications,Profile

def send_priority_email(name,receiver,title,message,author,neighbourhood):
  #Creating message subject and sender
  subject = title
  sender = 'mark.macharia@student.moringaschool.com'

  #passing in the context variables
  text_content = render_to_string('email/priority.txt',{"name":name,"title":title,"message":message,"author":author,"neighbourhood":neighbourhood})
  html_content = render_to_string('email/priority.html',{"name":name,"title":title,"message":message,"author":author,"neighbourhood":neighbourhood})

  msg = EmailMultiAlternatives(subject,text_content,sender,[receiver])
  msg.attach_alternative(html_content,'text/html')
  msg.send()