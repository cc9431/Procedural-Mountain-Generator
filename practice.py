from noise import perlin

#color = [0, 0, 0]
Xsize = 100
Ysize = 10
res  = 4.0
pnf  = perlin.SimplexNoise(period=6)
pnf.randomize()
img = ""

for y in range(Ysize):
	for x in range(Xsize):
		n = pnf.noise2(y / res, x / res)
		symbol = int(n / 2 * 255 + 0.5)
		if symbol > 0:
			img += "#"
		else:
			img += "."
		
	img += "\n"

print img
