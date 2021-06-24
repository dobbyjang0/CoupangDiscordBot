class NoneFormName(Exception):
    def __init__(self, form_name, message=None):
        self.form_name = form_name
        self.message = message

    @property
    def msg(self):
        return self.message

    def __str__(self):
        return "%s는 존재하지 않는 Form명입니다." % self.form_name.title() + " %s" % self.message if self.msg else ""


class InstanceHasNotSession(Exception):

    def __init__(self, msg):
        super().__init__(msg)
