from tqdm import tqdm
from PIL import Image
import time
import math
import sqlite3
import ColorName

"""Original Author: Larbi Sahli"""
"""
[important!]
if you are using IDLE remove tqdm from the for loops (tqdm(range())) in Acquire class and Analysis class
unless you are using more advanced text editor like PyCharm 

installing tqdm ==> pip install tqdm

visit for more information: https://pypi.org/project/tqdm/
---------------------

Geopixel is a program that can recognise geometrical shapes like :
[Ellipse, Circle, Rectangle, Square. Triangle, Right Triangle, Half ellipse, Half circle,  
Horizontal line, vertical line, line with angle, Curved line,  dot] 

Geopixle can recognise geometrical shapes with only analyzing each individual pixel
from a picture with one condition that the background color must be white to prevent the data overflow.

examples of how the picture that program can recognise in (Geometric shapes that pixel can recognise) folder.

>>initialize('Geometric shapes that pixel can recognise/Horizontal line')

initialize() is a method that start the program and the "Horizontal line" is the name of the picture
that has a Horizontal line shape in it, the program will process that picture and store the data
in a database table called "main_memory" the main_memory table will return the data list by calling display() method:

>>display('main_memory')

[(1, "{'type': 'Horizontal Line', 'width': '0.21 cm', 'length': '1.35 cm', 'color': 'Black'}")]

example with Ellipse:

>>initialize('Geometric shapes that pixel can recognise/Ellipse')
>>display('main_memory')

[(1, "{'type': 'Ellipse', 'Minor Axis': '2.34 cm', 'Major Axis': '6.64 cm', 'Circumference': '31.29 cm',
 'Area': '48.85 cm^2', 'color': 'Black'}")]


you can use multiple shapes in one picture but they must be vertical, 
see examples in (Geometric shapes that pixel can recognise) folder.

---------------------
_database main tables_

primitive_data : gathering primitive data (pixels)
processed_data : analyzing primitive data (pixels)
main_memory    : table that holds the final data list

"""

conn = sqlite3.connect('pixel_data.db')
c = conn.cursor()

"""Database management"""


class Table:

    def __init__(self, name):
        self.name = name

    def create_table(self):
        c.execute(f"""CREATE TABLE {self.name}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data STRING
        )""")

    def drop_table(self):
        sql = f"DROP TABLE {self.name}"
        c.execute(sql)

    def check_table(self):
        try:
            c.execute(f"select * from '{self.name}'")
            return True
        except sqlite3.Error:
            return False

    def shift_table(self):
        InsertData(1, 'processed_data_' + str(int(self.name.split('_')[2]) + 1), 'table_shift').update_data()


class InsertData:

    def __init__(self, _id_, _data_, name):
        self._id_ = _id_
        self._data_ = _data_
        self.name = name

    def insert_data(self):
        with conn:
            c.execute(f"INSERT INTO {self.name} VALUES (:id, :data)",
                      {'id': self._id_, 'data': self._data_})

    def update_data(self):
        with conn:
            c.execute(f"""UPDATE {self.name} SET data = :data WHERE id = :id""",
                      {'id': self._id_, 'data': self._data_})


class ExtractData:

    def __init__(self, _id_, name):
        self._id_ = _id_
        self.name = name

    def get_data(self):
        c.execute(f"SELECT * FROM {self.name} WHERE id= :id", {'id': self._id_})
        return c.fetchall()

    def check_data(self):
        if str(ExtractData(self._id_, self.name).get_data()) != '[]':
            return True
        else:
            return False


"""gathering primitive data (pixels)"""


class Acquire:
    """
    retrieve data
    insert data in database
    """

    def __init__(self, image):
        self.image = image

    def active_pixels_collector(self):
        photo = Image.open(self.image)  # your image
        photo = photo.convert('RGB')
        width = photo.size[0]  # define W and H
        height = photo.size[1]

        if not Table('primitive_data').check_table():
            Table('primitive_data').create_table()
        else:
            pass
        y_axis = 0  # height
        x_axis = 0  # width
        t_1 = time.perf_counter()  # -----------time---------->
        for y in tqdm(range(0, height)):  # each pixel has coordinates (x, y)  [remove tqdm if you are using IDLE]
            y_axis += 1
            for x in range(0, width):
                if photo.getpixel((x, y)) != (255, 255, 255):
                    x_axis += 1  # also act like a counter for inserting data id
                    rgb = photo.getpixel((x, y))
                    data = '(' + str(x) + ', ' + str(y) + ')' + ':' + str(rgb)
                    InsertData(x_axis, str(data), 'primitive_data').insert_data()
                else:
                    pass
        t_2 = time.perf_counter()
        if (t_2 - t_1) < 60:
            return f"{int(t_2 - t_1)} Seconds"
        elif 3600 > (t_2 - t_1) >= 60:
            s, minute = math.modf(((t_2 - t_1) / 60))
            if 120 > (t_2 - t_1):
                if int(s * 60) == 0:
                    return f"{int(minute)} Minute"
                else:
                    return f"{int(minute)} Minute and {int(s * 60)} Seconds"
            else:
                if int(s * 60) == 0:
                    return f"{int(minute)} Minutes"
                else:
                    return f"{int(minute)} Minutes and {int(s * 60)} Seconds"
        elif (t_2 - t_1) >= 3600:
            minutes, h = math.modf(((t_2 - t_1) / 60) / 60)
            if int(minutes * 60) == 0:
                return f"{int(h)} Hour"
            elif 3200 <= (t_2 - t_1):
                return f"{int(h)} Hour and {int(minutes * 60)} Minutes"
            else:
                return f"{int(h)} Hours and {int(minutes * 60)} Minutes"


"""Analysing Data"""


class Analysis:

    @staticmethod
    def cleaning():
        """
        preliminary  analysis
        cleaning data
        """
        c.execute("select * from 'primitive_data'")
        k = c.fetchall()
        line_counter = 0
        count = 0
        counter = 0
        counter_tear = 0
        if not Table('processed_data').check_table():
            Table('processed_data').create_table()
        else:
            pass
        for i in tqdm(range(1, len(k) - 1)):  # [remove tqdm if you are using IDLE]

            if eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[1] == \
                    eval((ExtractData(i + 1, 'primitive_data').get_data()[0][1].split(':')[0]))[1]:
                center = 0

                if count == 0:
                    first = ((eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[0]),
                             eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[1])
                    if not Table('save_value').check_table():
                        Table('save_value').create_table()
                        InsertData(1, str(first), 'save_value').insert_data()
                    else:
                        InsertData(1, str(first), 'save_value').update_data()

                if line_counter == 1:
                    first = (eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[0],
                             eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[1])
                    line_counter = 0
                    InsertData(1, str(first), 'save_value').update_data()

                if i == int(len(k) / 2):
                    center = eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[1]
                    if ExtractData(2, 'save_value').check_data():
                        InsertData(2, str(center), 'save_value').update_data()
                    else:
                        InsertData(2, str(center), 'save_value').insert_data()

                else:
                    pass

                if (eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[0]) + 1 != \
                        eval((ExtractData(i + 1, 'primitive_data').get_data()[0][1].split(':')[0]))[0]:

                    """identifying different lines"""
                    value_1 = eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[1]
                    value_2 = eval((ExtractData(i + 1, 'primitive_data').get_data()[0][1].split(':')[0]))[1]

                else:
                    value_1 = 0
                    value_2 = 0

                f_width = (count, eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[1])
                count += 1
                try:

                    if eval((ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0]))[1] != \
                            eval((ExtractData(i + 2, 'primitive_data').get_data()[0][1].split(':')[0]))[1]:
                        counter += 1
                        line_counter = 1
                        data = {'First': ExtractData(1, 'save_value').get_data()[0][1],
                                'y_center': center, 'F_width': f_width, 'ML': (value_1, value_2),
                                'RGB': ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[1]}
                        InsertData(counter, str(data), 'processed_data').insert_data()
                        count = 0
                    else:
                        pass
                except IndexError:
                    counter += 1
                    data = {'First': ExtractData(1, 'save_value').get_data()[0][1],
                            'y_center': ExtractData(2, 'save_value').get_data()[0][1],
                            'F_width': f_width, 'ML': (value_1, value_2),
                            'RGB': ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[1]}
                    InsertData(counter, str(data), 'processed_data').insert_data()

            else:
                counter_tear += 1
                value_1 = (ExtractData(i, 'primitive_data').get_data()[0][1].split(':')[0])
                value_2 = (ExtractData(i + 1, 'primitive_data').get_data()[0][1].split(':')[0])
                data = (value_1, value_2)
                if not Table('x_tear').check_table():
                    Table('x_tear').create_table()
                    InsertData(counter_tear, str(data), 'x_tear').insert_data()
                else:
                    InsertData(counter, str(data), 'x_tear').insert_data()

            if i + 2 == len(k):
                Table('save_value').drop_table()
            else:
                pass

        """SL/SSL"""
        c.execute("select * from 'processed_data'")
        w = c.fetchall()
        line_count = 0
        b_count = 0
        for i in range(1, len(w)):

            if eval(ExtractData(1, 'processed_data').get_data()[0][1])['ML'][0] == \
                    eval(ExtractData(i + 1, 'processed_data').get_data()[0][1])['ML'][0] and \
                    eval(ExtractData(i, 'processed_data').get_data()[0][1])['ML'][1] == \
                    eval(ExtractData(i + 1, 'processed_data').get_data()[0][1])['ML'][1]:

                if (eval(eval(ExtractData(i, 'processed_data').get_data()[0][1])['First'])[1]) + 1 == \
                        eval(eval(ExtractData(i + 1, 'processed_data').get_data()[0][1])['First'])[1]:
                    line_count += 1

                    data = eval(ExtractData(i, 'processed_data').get_data()[0][1])['First']
                    if not Table('save_value').check_table():
                        Table('save_value').create_table()
                        InsertData(1, str(data), 'save_value').insert_data()

                elif (eval(eval(ExtractData(i, 'processed_data').get_data()[0][1])['First'])[1]) + 1 != \
                        eval(eval(ExtractData(i + 1, 'processed_data').get_data()[0][1])['First'])[1]:

                    data = eval(ExtractData(i, 'processed_data').get_data()[0][1])['First']
                    if not Table('save_value').check_table():
                        Table('save_value').create_table()
                        InsertData(1, str(data), 'save_value').insert_data()

                    b_count += 1

                    if line_count == i + 1:
                        f_data = {"F/L": (ExtractData(1, 'save_value').get_data()[0][1],
                                          eval(ExtractData(i, 'processed_data').get_data()[0][1])['First']),
                                  'count': line_count + 1,
                                  'center': (
                                      (
                                          eval(
                                              ExtractData(int((int(line_count + 2) / 2) - 1),
                                                          'processed_data').get_data()[
                                                  0][
                                                  1])[
                                              'First']),
                                      (
                                          eval(
                                              ExtractData(int((int(line_count + 2) / 2) - 1),
                                                          'processed_data').get_data()[
                                                  0][
                                                  1])[
                                              'F_width'])),
                                  'RGB': ColorName.ColorNames.findNearestWebColorName(eval(
                                      eval(ExtractData(int((int(line_count + 2) / 2) - 1),
                                                       'processed_data').get_data()[0][1])['RGB']))}
                    else:

                        f_data = {"F/L": (ExtractData(1, 'save_value').get_data()[0][1],
                                          eval(ExtractData(i, 'processed_data').get_data()[0][1])['First']),
                                  'count': line_count + 1,
                                  'center': (
                                      (
                                          eval(ExtractData((i + 1) - int((int(line_count + 2) / 2)),
                                                           'processed_data').get_data()[0][
                                                   1])[
                                              'First']),
                                      (
                                          eval(ExtractData((i + 1) - int((int(line_count + 2) / 2)),
                                                           'processed_data').get_data()[0][
                                                   1])[
                                              'F_width'])),
                                  'RGB': ColorName.ColorNames.findNearestWebColorName(eval(
                                      eval(ExtractData((i + 1) - int((int(line_count + 2) / 2)),
                                                       'processed_data').get_data()[0][1])['RGB']))}

                    line_count = 0

                    if not Table('pre_value').check_table():
                        Table('pre_value').create_table()
                        InsertData(b_count, str(f_data), 'pre_value').insert_data()
                    else:
                        InsertData(b_count, str(f_data), 'pre_value').insert_data()

                    Table('save_value').drop_table()

                if i + 1 == len(w):

                    f_data = {"F/L": (ExtractData(1, 'save_value').get_data()[0][1],
                                      eval(ExtractData(i + 1, 'processed_data').get_data()[0][1])['First']),
                              'count': line_count + 2,
                              'center': (
                                  (eval(ExtractData((i + 3) - int((int(line_count + 3) / 2)),
                                                    'processed_data').get_data()[
                                            0][1])[
                                      'First']),
                                  (eval(ExtractData((i + 3) - int((int(line_count + 3) / 2)),
                                                    'processed_data').get_data()[
                                            0][1])[
                                      'F_width'])),
                              'RGB': ColorName.ColorNames.findNearestWebColorName(eval(
                                  eval(ExtractData((i + 3) - int((int(line_count + 3) / 2)),
                                                   'processed_data').get_data()[0][1])['RGB']))}

                    line_count = 0

                    if not Table('pre_value').check_table():
                        Table('pre_value').create_table()
                        InsertData(b_count + 1, str(f_data), 'pre_value').insert_data()
                    else:
                        InsertData(b_count + 1, str(f_data), 'pre_value').insert_data()

                    Table('save_value').drop_table()

                else:
                    pass
            else:
                pass


class Recognition:

    @staticmethod
    def insert_main_memory(i, data):
        if not Table('main_memory').check_table():
            Table('main_memory').create_table()
            InsertData(i, str(data), 'main_memory').insert_data()
        else:
            InsertData(i, str(data), 'main_memory').insert_data()

    @staticmethod
    def active():
        Analysis.cleaning()
        if Table('pre_value').check_table():
            c.execute("select * from 'pre_value'")
        data_list = c.fetchall()
        for i in range(1, len(data_list) + 1):
            _width_ = eval(ExtractData(i, 'processed_data').get_data()[0][1])['F_width'][0]
            if (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) <= 9 and \
                    (eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1])[0] <= 9:

                """Dot"""
                _type = "Dot"
                _data = {'Type': _type, 'color': (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])}
                Recognition.insert_main_memory(i, _data)

            elif eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[1] >= 10 and \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1] >= 10 and \
                    6 >= abs((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] -
                              eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0])) >= 0 and \
                    (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) <= 10:
                """Straight Line"""

                _type = "Horizontal Line"
                _width = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) * 0.0264583333
                _length = (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0]) * 0.0264583333
                _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                _data = {'type': _type, 'width': str(round(_width, 2)) + ' cm',
                         'length': str(round(_length, 2)) + ' cm', 'color': _color}
                Recognition.insert_main_memory(i, _data)

            elif eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1][0] <= 10 and \
                    5 >= abs((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] -
                              eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0])) >= 0 and \
                    (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) > 20 and \
                    eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1][1] + 3 >= (
                    (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[1] +
                     eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1])) / 2 >= \
                    eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1][1] - 3 \
                    and eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0] > \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] + 5:
                _diameter = abs(eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1] -
                                eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[
                                    1])
                a = ((eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) / 2)
                b = abs((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0]) -
                        (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0]))/2

                if abs(a - b) > 5:

                    """Half Ellipse"""
                    _type = "Half Ellipse"

                    def _choice(x):
                        if x == 'big':
                            if a > b:
                                return a
                            else:
                                return b
                        elif x == 'small':
                            if a < b:
                                return a
                            else:
                                return b
                    area = math.pi * (a * 0.0264583333) * (b * 0.0264583333)

                    _circum = 2*math.pi*math.sqrt((a**2+b**2)/2)*0.0264583
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])

                    _data = {'type': _type, 'Minor Axis': str(round((_choice('small') * 0.0264583333), 2)) + ' cm',
                             'Major Axis': str(round(_choice('big') * 0.0264583333, 2)) + ' cm',
                             'Circumference': str(round(_circum / 2, 2)) + ' cm',
                             'Area': str(round(area/2, 2)) + ' cm^2', 'color': _color}
                    Recognition.insert_main_memory(i, _data)

                else:
                    """Half Circle"""
                    _type = "Half Circle"

                    _circum = (2 * math.pi * _diameter * 0.0264583333) / 2

                    area = (math.pi * ((_diameter * 0.0264583333) / 2) ** 2) / 2
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                    _data = {'type': _type, 'Diameter': str(round(_diameter * 0.0264583333, 2)) + ' cm',
                             'Circumference': str(round(_circum, 2)) + ' cm', 'Area': str(round(area, 2)) + ' cm^2',
                             'color': _color}
                    Recognition.insert_main_memory(i, _data)

            elif eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1][0] <= 10 and \
                    5 >= abs((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] -
                              eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0])) >= 0 and \
                    (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) > 20 and \
                    eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1][1] + 3 >= (
                    (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[1] +
                     eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1])) / 2 >= \
                    eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1][1] - 3 and \
                    (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0]) < \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0] + 5:

                """Vertical Line"""
                _type = "Vertical Line"
                _width = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1][0] + 1) * 0.0264583333
                _length = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) * 0.0264583333
                _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                _data = {'type': _type, 'width': str(round(_width, 2)) + ' cm',
                         'length': str(round(_length, 2)) + ' cm', 'color': _color}
                Recognition.insert_main_memory(i, _data)

            elif 6 >= abs(((((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1]) -
                             (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[1])) -
                            (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count'])))) >= 0 and \
                    abs(((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1]) -
                         (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[1]))) >= 20 and \
                    abs(((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0]) -
                         (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0]))) >= 20 and \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] > \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0] > \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0] or \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0] > \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0] > \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0]:
                """Line with Angle"""

                if Table('x_tear').check_table():

                    try:
                        value = eval(eval(ExtractData(((eval(ExtractData(i,
                                                                         'pre_value').get_data()[0][1])['count']) / 2)
                                                      + 1, 'x_tear').get_data()[0][1])[0])[0]

                    except IndexError:
                        value = 0
                else:
                    value = 0

                opp = abs(((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1]) -
                           (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[1])))
                adj = abs(((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0]) -
                           (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0])))
                hyp = math.sqrt((opp ** 2) + (adj ** 2))
                angle = math.acos(adj / hyp) * (180 / math.pi)

                if (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0]) > \
                        (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0]) and value == 0:

                    """Acute Angle Line"""
                    _type = "Acute Angle Line"
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                    _data = {'type': _type, 'angle': str(round(angle, 2)) + ' degree',
                             'length': str(round(hyp * 0.0264583333, 2)) + ' cm', 'color': _color}
                    Recognition.insert_main_memory(i, _data)

                elif (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0]) > \
                        (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0]) and value == 0:
                    """Obtuse Angle Line"""
                    _type = "Obtuse Angle Line"
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                    _data = {'type': _type, 'angle': str(180 - round(angle, 2)) + ' degree',
                             'length': str(round(hyp * 0.0264583333, 2)) + ' cm', 'color': _color}
                    Recognition.insert_main_memory(i, _data)

                elif value > 0:
                    """triangle"""
                    _type = "Triangle"
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                    _data = {'type': _type, 'color': _color}
                    Recognition.insert_main_memory(i, _data)

            elif (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0]) > \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0] and \
                    (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0]) > \
                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0] and \
                    ((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1]) +
                     (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[1])) / 2 <= \
                    (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[1]) + 2 and \
                    (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) > 30:

                if (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) / 2 >= abs(
                        (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0]) -
                        (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0])) <= \
                        ((eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) / 2) - 10 or \
                        abs((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0]) -
                            (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0])) > \
                        ((eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) / 2) <= abs(
                    (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0]) - (eval(
                        eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0])) - 10:

                    """Ellipse"""
                    _diameter = abs(eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1] -
                                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[
                                        1]) * 0.0264583333

                    a = ((eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) / 2)
                    b = abs((eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0]) -
                            (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0])) / 2

                    def choice(x):
                        if x == 'big':
                            if a > b:
                                return a
                            else:
                                return b
                        elif x == 'small':
                            if a < b:
                                return a
                            else:
                                return b

                    area = math.pi * (a * 0.0264583333) * (b * 0.0264583333)

                    _circum = 2*math.pi*math.sqrt((a**2+b**2)/2)*0.0264583

                    _type = "Ellipse"
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])

                    _data = {'type': _type, 'Minor Axis': str(round((choice('small') * 0.0264583333), 2)) + ' cm',
                             'Major Axis': str(round(choice('big') * 0.0264583333, 2)) + ' cm',
                             'Circumference': str(round(_circum, 2)) + ' cm', 'Area': str(round(area, 2)) + ' cm^2',
                             'color': _color}
                    Recognition.insert_main_memory(i, _data)
                else:
                    """circle"""
                    _diameter = abs(eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1] -
                                    eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[
                                        1]) * 0.0264583333
                    _circum = 2 * math.pi * _diameter
                    area = math.pi * (_diameter / 2) ** 2
                    _type = "Circle"
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])

                    _data = {'type': _type, 'Diameter': str(round(_diameter, 2)) + ' cm',
                             'Circumference': str(round(_circum, 2)) + ' cm', 'Area': str(round(area, 2)) + ' cm^2',
                             'color': _color}
                    Recognition.insert_main_memory(i, _data)

            elif eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] == \
                eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0] and \
                eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] == \
                (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0]) and \
                    (eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][1])[0] < 18 or(
                    abs(eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] -
                        eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[0]) < 8 and
                    abs(eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[0] -
                        (eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['center'][0])[0])) < 20):

                if abs(_width_ - (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count'])) > 10 and \
                        _width_ > 15:
                    """Rectangle"""
                    _type = "Rectangle"

                    length = _width_ * 0.0264583333
                    width = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) * 0.0264583333
                    area = _width_ * (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) * 0.0264583333
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                    _data = {'type': _type, 'Length': str(round(length, 2))+' cm', 'Width': str(round(width, 2))+' cm',
                             'Area': str(round(area, 2)) + ' cm^2', 'color': _color}
                    Recognition.insert_main_memory(i, _data)
                elif abs(_width_ - (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count'])) <= 10 and \
                        _width_ > 15:
                    """Square"""
                    _type = "Square"
                    length = (_width_+2) * 0.0264583333
                    width = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) * 0.0264583333
                    area = _width_ * (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) * 0.0264583333
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                    _data = {'type': _type, 'Length': str(round(length, 2))+' cm', 'Width': str(round(width, 2))+' cm',
                             'Area': str(round(area, 2)) + ' cm^2', 'color': _color}
                    Recognition.insert_main_memory(i, _data)
                else:

                    """Right triangle"""
                    _type = "Right triangle"
                    adj = abs(eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][0])[1] -
                              eval(eval(ExtractData(i, 'pre_value').get_data()[0][1])['F/L'][1])[1]) * 0.0264583333
                    opp = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['count']) * 0.0264583333
                    hyp = math.sqrt((opp ** 2) + (adj ** 2))
                    angle = math.acos(adj / hyp) * (180 / math.pi)

                    area = (1/2)*adj*opp
                    _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                    _data = {'type': _type, 'Adjacent': str(round(adj, 2)) + ' cm',
                             'Hypotenuse': str(round(hyp, 2)) + ' cm',
                             'Opposite': str(round(opp, 2)) + ' cm',
                             'Area': str(round(area, 2)) + ' cm^2', 'Angle': str(round(angle, 2))+' degree',
                             'color': _color}
                    Recognition.insert_main_memory(i, _data)

            else:
                """Curved Line"""
                _type = "Curved Line"
                _color = (eval(ExtractData(i, 'pre_value').get_data()[0][1])['RGB'])
                _data = {'type': _type, 'color': _color}
                Recognition.insert_main_memory(i, _data)

        Table('pre_value').drop_table()
        Table('processed_data').drop_table()
        Table('primitive_data').drop_table()
        Table('x_tear').drop_table()


def display(name):
    if Table(f"{name}").check_table():
        c.execute(f"select * from '{name}'")
    print(c.fetchall())


if __name__ == "__main__":
    def initialize(name):
        print(Acquire(f"{name}.png").active_pixels_collector())
        if Table('main_memory').check_table():
            Table('main_memory').drop_table()
        Recognition.active()

    initialize('Geometric shapes that pixel can recognise/Horizontal line')
    display('main_memory')
    c.close()
