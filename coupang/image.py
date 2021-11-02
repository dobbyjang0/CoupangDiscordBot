import io

__all__ = ('Image',)


class Image:

    def __init__(self, fp):

        if isinstance(fp, io.IOBase):
            self.fp = fp

        else:
            self.fp = open(fp, 'rb')
