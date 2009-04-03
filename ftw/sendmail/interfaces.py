class IHTMLComposer():
    """An HTML composer.
    """

    from_name = schema.TextLine(
        title=_(u"From name"),
        description=_(u"The sender name that will appear in messages sent from this composer."),
        required=False,
        )
    from_address = schema.TextLine(
        title=_(u"From address"),
        description=_(u"The from addess that will appear in messages sent from this composer."),
        required=False,
        )
    subject = schema.TextLine(
        title=_(u"Message subject"),
        description=_(u"You may use a number of variables here, like "
                      "${site-title}."),
        required=False,
        )
    replyto_address = schema.TextLine(
        title=_(u"Reply-to address"),
        description=_(u"The reply-to addess that will appear in messages sent from this composer."),
        required=False,
        )
    header_text = schema.Text(
        title=_(u"Header text"),
        description=_(u"Text to appear at the beginning of every message. "
                      "You may use a number of variables here including "
                      "${subject}."),
        required=False,
        )
    footer_text = schema.Text(
        title=_(u"Footer text"),
        description=_(u"Text to appear at the end of every message"),
        required=False,
        )
    stylesheet = schema.Text(
        title=_(u"CSS Stylesheet"),
        description=_(u"The stylesheet will be applied to the document."),
        required=False,
        )