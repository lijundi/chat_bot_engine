# @Time : 2020/4/15 21:51 
# @Author : lijundi
# @File : file_opt.py 
# @Software: PyCharm


def format_write(_file, title, _list=None, blank=0, start='', end=''):
    """
    :param start:
    :param end:
    :param blank:
    :param _list:
    :param title:
    :type _file: file
    """
    # _file为被写入的文件对象
    # title为第一行的内容
    # _list为以“-”开头的内容，如果为空则不写
    # blank表示写每一行前需要添加的空格数
    # start表示整段内容前面需要添加的字符串
    # end表示整段内容最后需要添加的字符串
    _file.write(start)
    if _list is None:
        _list = []
    head = ''
    for i in range(0, blank):
        head += ' '
    _file.write(head+title+'\n')
    for i in _list:
        _file.write(head+'  - '+i+'\n')
    _file.write(end)

