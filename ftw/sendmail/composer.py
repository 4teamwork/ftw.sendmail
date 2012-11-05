import formatter
import string
import StringIO
import htmllib
import stoneagehtml
import zope.sendmail.mailer
from zope import component
from zope import interface
import persistent
import email
from email.Utils import formataddr
from email import Encoders
from email.Header import Header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.Utils import formatdate
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

import Products.CMFPlone.interfaces

from ftw.sendmail.interfaces import IEMailComposer

_ = lambda x: x

def _render_cachekey(method, self, vars):
    return (vars)

def create_html_mail(subject, html, text=None, from_addr=None, to_addr=None,
                     headers=None, encoding='UTF-8', attachments=[]):
    """Create a mime-message that will render HTML in popular
    MUAs, text in better ones.
    """
    # Use DumbWriters word wrapping to ensure that no text line
    # is longer than plain_text_maxcols characters.
    plain_text_maxcols = 72

    html = html.encode(encoding)
    if text is None:
        # Produce an approximate textual rendering of the HTML string,
        # unless you have been given a better version as an argument
        textout = StringIO.StringIO()
        formtext = formatter.AbstractFormatter(formatter.DumbWriter(
                        textout, plain_text_maxcols))
        parser = htmllib.HTMLParser(formtext)
        parser.feed(html)
        parser.close()

        # append the anchorlist at the bottom of a message
        # to keep the message readable.
        counter = 0
        anchorlist  = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
        for item in parser.anchorlist:
            counter += 1
            anchorlist += "[%d] %s\n" % (counter, item)

        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist
    else:
        text = text.encode(encoding)

    # if we would like to include images in future, there should
    # probably be 'related' instead of 'mixed'
    msg = MIMEMultipart('mixed')
    # maybe later :)  msg['From'] = Header("%s <%s>" % (send_from_name, send_from), encoding)
    msg['Subject'] = Header(subject, encoding)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate(localtime=True)
    msg["Message-ID"] = email.Utils.make_msgid()
    if headers:
        for key, value in headers.items():
            msg[key] = value
    msg.preamble = 'This is a multi-part message in MIME format.'



    alternatives = MIMEMultipart('alternative')
    msg.attach(alternatives)
    alternatives.attach( MIMEText(text, 'plain', _charset=encoding) )
    alternatives.attach( MIMEText(html, 'html',  _charset=encoding) )

    #add the attachments
    for f, name, mimetype in attachments:
          if mimetype is None:
              mimetype = ('application', 'octet-stream')
          maintype, subtype = mimetype
          if maintype == 'text':
              # XXX: encoding?
              part = MIMEText(f.read(), _subtype=subtype)
          else:
              part = MIMEBase(maintype, subtype)
              part.set_payload(f.read())
              Encoders.encode_base64(part)
          part.add_header('Content-Disposition', 'attachment; filename="%s"' % name)
          msg.attach(part)

    return msg

class HTMLComposer(persistent.Persistent):
    # """
    #   >>> from zope.interface.verify import verifyClass
    #   >>> from collective.dancing.interfaces import IHTMLComposer
    #   >>> verifyClass(IHTMLComposer, HTMLComposer)
    #   True
    # """

    interface.implements(IEMailComposer)

    title = _(u'HTML E-Mail')

    def __init__(self, message, subject, to_addresses, from_name=u'', from_address='', stylesheet='', replyto_address=''):
        properties = component.getUtility(
            Products.CMFCore.interfaces.IPropertiesTool)
        self.encoding = properties.site_properties.getProperty('default_charset', 'utf-8')
        self.stylesheet = stylesheet
        self.from_name = from_name or properties.email_from_name
        self.from_address = from_address or properties.email_from_address
        self.to_addresses = to_addresses and to_addresses or None
        self.replyto_address = replyto_address
        self.subject = subject
        self.message = message
        self.header_text = u""
        self.footer_text = u""

    template = ViewPageTemplateFile('browser/composer-html.pt')

    context = None
    @property
    def request(self):
        site = zope.app.component.hooks.getSite()
        return site.REQUEST

    def _prepare_address(self, name, mail, charset):
        if not isinstance(name, unicode):
            name = name.decode(charset)
        if not isinstance(mail, unicode):
            # mail has to be be ASCII!!
            mail = mail.decode(charset).encode('us-ascii', 'replace')
            #TODO : assert that mail is now valid. (could have '?' from repl.)
        return formataddr((str(Header(name, charset)), mail))

    @property
    def _from_address(self):
        return self._prepare_address(self.from_name, self.from_address, self.encoding)

    @property
    def _to_addresses(self):
        addresses = []
        for name, mail in self.to_addresses:
            addresses.append(self._prepare_address(name, mail, self.encoding))
        return ', '.join(addresses)

    @property
    def _replyto_address(self):
        name, mail = self.replyto_address
        return self._prepare_address(name, mail, self.encoding)

    @property
    def language(self):
        return self.request.get('LANGUAGE')

    def _vars(self):
        """Provide variables for the template.

        Override this or '_more_vars' in your custom HTMLComposer to
        pass different variables to the templates.
        """
        vars = {}
        site = component.getUtility(Products.CMFPlone.interfaces.IPloneSiteRoot)
        #site = utils.fix_request(site, 0)
        fix_urls = lambda t: t #lambda t: transform.URL(site).__call__(t, subscription)

        vars['site_url'] = site.absolute_url()
        vars['site_title'] = unicode(site.Title(), 'UTF-8')
        vars['subject'] = self.subject
        vars['message'] = self.message
        # Why would header_text or footer_text ever be None?
        vars['header_text'] = fix_urls(self.header_text or u"")
        vars['footer_text'] = fix_urls(self.footer_text or u"")
        vars['stylesheet'] = self.stylesheet
        vars['from_addr'] = self._from_address
        vars['to_addr'] = self._to_addresses
        headers = vars['more_headers'] = {}
        if self.replyto_address:
            headers['Reply-To'] = self._replyto_address

        # It'd be nice if we could use an adapter here to override
        # variables.  We'd probably want to pass 'items' along to that
        # adapter.

        return vars


    #@volatile.cache(_render_cachekey)
    def _html(self, vars, **kwargs):
        html = self.template(**vars)
        return stoneagehtml.compactify(html, **kwargs).decode('utf-8')

    def html(self, override_vars=None, template_vars={}, **kwargs):

        vars = self._vars()

        if override_vars is None:
            override_vars = {}
        vars.update(override_vars)

        html = self._html(vars, **kwargs)
        html = string.Template(html).safe_substitute(template_vars)
        return html

    def render(self, override_vars=None, template_vars={}, attachments=[], **kwargs):

        vars = self._vars()

        if override_vars is None:
            override_vars = {}
        vars.update(override_vars)

        message = create_html_mail(
            vars['subject'],
            self.html(override_vars=override_vars,template_vars=template_vars,**kwargs),
            from_addr=vars['from_addr'],
            to_addr=vars['to_addr'],
            headers=vars.get('more_headers'),
            encoding=self.encoding,
            attachments=attachments)

        return message

class SMTPMailer(zope.sendmail.mailer.SMTPMailer):
    """A mailer for use with zope.sendmail that fetches settings from
    the Plone site's configuration.
    """

    def _fetch_settings(self):
        root = component.getUtility(Products.CMFPlone.interfaces.IPloneSiteRoot)
        m = root.MailHost
        return dict(hostname=m.smtp_host or 'localhost',
                    port=m.smtp_port,
                    username=getattr(m, 'smtp_userid', None) or m.smtp_uid or None,
                    password=getattr(m, 'smtp_pass', None) or m.smtp_pwd or None,)

    def update_settings(self):
        self.__dict__.update(self._fetch_settings())

    def send(self, fromaddr, toaddrs, message):
        return super(SMTPMailer, self).send(fromaddr, self._split(toaddrs), message)

    @staticmethod
    def _split(value):
        """
          >>> split = SMTPMailer._split
          >>> split('"Daniel flash, Nouri" <daniel.nouri@gmail.com>')
          ['"Daniel flash, Nouri" <daniel.nouri@gmail.com>']
          >>> split('Daniel Nouri <daniel.nouri@gmail.com>, '
          ...       'Daniel Widerin <daniel.widerin@kombinat.at>')
          ['Daniel Nouri <daniel.nouri@gmail.com>', 'Daniel Widerin <daniel.widerin@kombinat.at>']
          >>> split('"Daniel flash, dance Nouri" <daniel.nouri@gmail.com>,'
          ...       '"Daniel Saily Widerin" <daniel.widerin@kombinat.at>')
          ['"Daniel flash, dance Nouri" <daniel.nouri@gmail.com>', '"Daniel Saily Widerin" <daniel.widerin@kombinat.at>']
        """
        items = []
        last_index = 0
        for i, c in enumerate(value):
            if c == ',':
                if value[:i].count('"') % 2 == 0:
                    items.append(value[last_index:i].strip())
                    last_index = i + 1
        last_item = value[last_index:]
        if last_item.strip():
            items.append(last_item.strip())
        return items
