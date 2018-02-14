import pyexcel


class ExcelFile:
    def __init__(self, file_name):
        self.sheet = None
        self.file_name = file_name
        self.__set_file_type()
        self.__set_file_sheet()
        self.__set_number_of_records()

    def __set_file_type(self):
        file_extension = str(self.file_name.split('.')[1])
        self.file_type = file_extension.upper()

    def __set_file_sheet(self):
        if self.file_type == 'CSV':
            self.sheet = pyexcel.get_array(file_name= self.file_name)
        elif self.file_type == 'XLSX':
            pass
        elif self.file_type == 'XLS':
            pass

    def __set_number_of_records(self):
        if self.sheet is not None:
            self.num_of_records = len(self.sheet)
        else:
            self.num_of_records = 0

    def get_header(self):
        if self.sheet is not None:
            return self.sheet[0]
        else:
            return None

    def get_num_of_records(self):
        return self.num_of_records

    def get_records(self, exclude_header=False):
        if exclude_header is True:
            return self.sheet[1: ]
        return self.sheet


