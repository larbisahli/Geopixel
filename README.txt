Geopixel is a program that can recognise geometrical shapes like :
[Ellipse, Circle, Rectangle, Square. Triangle, Right Triangle, Half ellipse, Half circle,  
Horizontal line, vertical line, line with angle, Curved line,  dot] 

Geopixle can recognise geometrical shapes with only analyzing each individual pixel from a picture with one condition that the background color 
must be white to prevent the data overflow.

examples of how the picture that program can recognise in (Geometric shapes that pixel can recognise) folder.

>>initialize('Geometric shapes that pixel can recognise/Horizontal line')

initialize() is a method that start the program and the "Horizontal line" is the name of the picture that has a Horizontal line shape in it ,
the program will process that picture and store the data in a database table called "main_memory" the main_memory table will return the data 
list by calling display() method:

>>display('main_memory')

[(1, "{'type': 'Horizontal Line', 'width': '0.21 cm', 'length': '1.35 cm', 'color': 'Black'}")]

same with Ellipse:

>>initialize('Geometric shapes that pixel can recognise/Ellipse')
>>display('main_memory')

[(1, "{'type': 'Ellipse', 'Minor Axis': '2.34 cm', 'Major Axis': '6.64 cm', 'Circumference': '31.29 cm', 'Area': '48.85 cm^2', 'color': 'Black'}")]


you can use multiple shapes in one picture but they must be vertical see examples in (Geometric shapes that pixel can recognise) folder.