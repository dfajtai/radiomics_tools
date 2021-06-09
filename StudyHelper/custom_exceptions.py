NoneType = type(None)


class CrucialFileMissingError(Exception):
    def __init__(self, file_meaning = None, file_path = None):
        super(CrucialFileMissingError, self).__init__("Crucial file missing")
        self.file_meaning = file_meaning
        self.file_path = file_path

    def __str__(self):
        err_string = ""
        if not isinstance(self.file_meaning, NoneType):
            err_string = "{0} missing".format(str(self.file_meaning))
            if not isinstance(self.file_path, NoneType):
                err_string += " at '{0}'".format(str(self.file_path))

        if len(err_string)>0:
            return err_string
        else:
            return super(CrucialFileMissingError, self).__str__()