import os
import urllib
import zipfile
import numpy as np
import pandas as pd


class FileProcessor:
    def __init__(self):
        self._default_path = './app/data/'
        self._downloaded = False
        self._extracted = False

    def download_file(self, url, file_to_save=None):
        """
        Method that downloads file from specified URL
        :param url: URL from which the file will be downloaded
        :type url: str
        :param file_to_save: path to save downloaded file
        :type file_to_save: str

        :return: download stats (success or not)
        :rtype: str
        """
        if file_to_save is None:
            path = os.path.join(self._default_path, 'downloaded')
            file_to_save = path
        try:
            urllib.request.urlretrieve(url, file_to_save)
        except urllib.error.HTTPError as e:
            return str(e)
        else:
            self.downloaded_path_ = file_to_save
            self._downloaded = True
            self.url_ = url
            return 'Success!'

    def unzip_file(self, path_to_archive=None, path_to_extract=None):
        """
        Method that unzips zip archive to specified directory

        :param path_to_archive: path to archive file
        :type path_to_archive: str
        :param path_to_extract: path to existing directory for extraction
        :type path_to_extract: str

        :return: unzip status (success or not)
        :rtype: str
        """

        if path_to_archive is None:
            if self._downloaded:
                path_to_archive = self.downloaded_path_
            else:
                return 'Error: path_to_archive must be specified'

        if path_to_extract is None:
            path_to_extract = self._default_path

        if not os.path.isdir(path_to_extract):
            return "Error: path_to_extract must be a directory"
        if not os.path.isfile(path_to_archive):
            return "Error: path_to_archive must be a file"
        try:
            with zipfile.ZipFile(path_to_archive, 'r') as zip_ref:
                zip_ref.extractall(path_to_extract)
                self.extracted_names_ = zip_ref.namelist()
                self._extracted = True
        except OSError as e:
            return str(e)
        else:
            return 'Success!'

    def parse_file(self, path_to_file=None):
        """
        Method that parses files with the following strcture:

        @relation winequality-red
        @attribute attr1
        ...
        @attribute attrn
        @inputs <Input Columns>
        @outputs <Output Column>
        @data
        <regular csv data>


        :param path_to_file: path to file that will be parsed
        :type path_to_file: string
        :return: dataframe with data from file
        :rtype: pandas.DataFrame
        """

        if path_to_file is None:
            if self._extracted:
                path = os.path.join(self._default_path, self.extracted_names_[-1])
                path_to_file = path
            else:
                return FileNotFoundError('path_to_file must be specified')
        with open(path_to_file) as f:
            raw_data = f.read()
        data = [row.split() for row in raw_data.split('@')][1:]
        clean_data = {field[0]: field[1:] for field in data}
        data_to_df = [row.split(',') for row in clean_data['data']]
        columns = clean_data['inputs'] + clean_data['outputs']
        columns = [colname.strip(', ') for colname in columns]
        df = pd.DataFrame(data=data_to_df, columns=columns, dtype=np.float64)
        return df

    def do_all(self, url):
        """
        Method that does all transformations with default parameters

        :param url: URL from which the file will be downloaded
        :type url: str

        :return: dataframe with data from file
        :rtype: pandas.DataFrame
        """
        self.download_file(url)
        self.unzip_file()
        parsed = self.parse_file()
        return parsed


if __name__ == "__main__":
    processor = FileProcessor()
    url = r'https://sci2s.ugr.es/keel/dataset/data/classification/winequality-red.zip'
    processor.do_all(url)
    print('Done!')
