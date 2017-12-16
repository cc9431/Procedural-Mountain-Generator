import numpy
import random
from PIL import Image
r = (random.randrange(0, 255))
g = (random.randrange(0, 255))
b = (random.randrange(0, 255))

output = [[(r, g, b) for x in range(100)] for y in range(100)]

output = numpy.array(output, dtype=numpy.uint8)

new_image = Image.fromarray(output)
new_image.show()