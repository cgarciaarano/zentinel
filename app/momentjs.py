#
# Just a Python wrapper to JS Moment
#
from jinja2 import Markup

class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def getTimestamp(self):
        return self.timestamp.isoformat() + ' +0000'

    def render(self, format):
        return Markup("<script>\ndocument.write(moment(\"%s\",\"YYYY-MM-DDTHH:mm:ss.SSS Z\").%s);\n</script>" % (self.getTimestamp(), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")