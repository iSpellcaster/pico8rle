#!/usr/bin/env python	
from PIL import Image
import argparse
import math

pals = [[
 [0x00,0x00,0x00],
 [0x1d,0x2b,0x53],
 [0x7e,0x25,0x53],
 [0x00,0x87,0x51],
 [0xab,0x52,0x36],

 [0x5f,0x57,0x4f],
 [0xc2,0xc3,0xc7],
 [0xff,0xf1,0xe8],
 [0xff,0x00,0x4d],
 [0xff,0x00,0x4d],

 [0xff,0xec,0x27],
 [0x00,0xe4,0x36],
 [0x29,0xad,0xff],
 [0x29,0xad,0xff],
 [0xff,0x77,0xa8],

 [0xff,0xcc,0xaa],
],[
 [0x29,0x18,0x14],
 [0x29,0x18,0x14],
 [0x42,0x21,0x36],
 [0x42,0x21,0x36],

 [0x74,0x2f,0x29],
 [0x49,0x33,0x3b],
 [0xa2,0x88,0x79],
 [0xf3,0xef,0x7d],
 [0xbe,0x12,0x50],

 [0xff,0x6c,0x24],
 [0xa8,0xe7,0x2e],
 [0xa8,0xe7,0x2e],
 [0x06,0x5a,0xb5],
 [0x75,0x46,0x65],

 [0xff,0x6e,0x59],
 [0xff,0x9d,0x81],
],[
 [0x00,0x00,0x00],
 [0x1d,0x2b,0x53],
 [0x7e,0x25,0x53],
 [0x00,0x87,0x51],
 [0xab,0x52,0x36],

 [0x5f,0x57,0x4f],
 [0xc2,0xc3,0xc7],
 [0xff,0xf1,0xe8],
 [0xff,0x00,0x4d],
 [0xff,0x00,0x4d],

 [0xff,0xec,0x27],
 [0x00,0xe4,0x36],
 [0x29,0xad,0xff],
 [0x29,0xad,0xff],
 [0xff,0x77,0xa8],

 [0xff,0xcc,0xaa],
 [0x29,0x18,0x14],
 [0x29,0x18,0x14],
 [0x42,0x21,0x36],
 [0x42,0x21,0x36],

 [0x74,0x2f,0x29],
 [0x49,0x33,0x3b],
 [0xa2,0x88,0x79],
 [0xf3,0xef,0x7d],
 [0xbe,0x12,0x50],

 [0xff,0x6c,0x24],
 [0xa8,0xe7,0x2e],
 [0xa8,0xe7,0x2e],
 [0x06,0x5a,0xb5],
 [0x75,0x46,0x65],

 [0xff,0x6e,0x59],
 [0xff,0x9d,0x81],
]]

result = [None] * (128*128)
counts = [None] * 32
bestcolor = []
outputFormat='x'
compact=False

def bestmatch(rgb, pal):	
	r, g, b = rgb
	color_diffs = []
	index = 0
	for color in pal:
		cr, cg, cb = color
		color_diff = abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2
		color_diffs.append((color_diff, index))
		index = index +1
	return min(color_diffs)[1]

def getcolors(im, pal):
	w,h = im.size
	
	y = 0
	while y in range(0,h):
		x = 0
		while x in range(0,w):
			col = bestmatch(im.getpixel( (x,y) ),pal)
			rgb = (pal[col][0], pal[col][1],pal[col][2])
			im.putpixel((x,y), rgb)
			result[x+y*w] = col
			if counts[col]:
				counts[col] = counts[col]+1
			else:
				counts[col] = 1
			x = x + 1
		#end while x			
		y = y + 1
	#end while y
#end getcolors

def formatRLE(col,run):
	colRun = col << 8 | run
	if compact:
		strval = base64encode(colRun)
		while len(strval) < 2:
			strval = "0"+strval
	else:
		strval = format(colRun,outputFormat)
	
	return strval
	#return format(col,outputFormat) + "," + format(run,outputFormat)

def rle():
	rleCode = "\""
	y = 0
	while y in range(0,128):
		x = 0
		run = 0
		col = result[x+y*128]
		while x in range(0,128):
			if col == result[x+y*128]:
				run = run+1
			else:
				rleCode = rleCode + formatRLE(col,run)
				if not compact:
					rleCode =rleCode+ ","
				#rleCode = rleCode + format(col,outputFormat) + "," + format(run,outputFormat) + ","
				#rleCode = rleCode + chr(col) + chr(run)
				
				col = result[x+y*128]
				run = 1
			x = x + 1
		#end while x
		if (y <127):
			#rleCode = rleCode + chr(col) + chr(run)
			rleCode = rleCode + formatRLE(col,run)
			if not compact:
				rleCode =rleCode+ ","
			#rleCode = rleCode + format(col,outputFormat) + "," + format(run,outputFormat) + ","
		else:
			#rleCode = rleCode + chr(col) + chr(run)+ "\""
			rleCode = rleCode + formatRLE(col,run)+ "\""
			

			#rleCode = rleCode + format(col,outputFormat) + "," + format(run,outputFormat) + "\""
		y = y + 1
	#end while y
	return rleCode

def base64encode(value):
	base64str='0123456789abcdefghijklmnopqrstuvwxyz!@#$%^&*()_-+=[]}{;:<>,./?~|'
	b64result=""
	if value == 0:
		return "00"
	else:
		while value > 0:
			i=value%64
			b64result=base64str[i:i+1] + b64result
			value=math.floor(value/64)
		return b64result

def createpal(bestcolor, pal):
	optimal = sorted(bestcolor, key=lambda col: col[1], reverse=True)
	newpal = []
	palstr="\""
	#print(optimal)
	#print(len(optimal))
	#print("---")
	max = min(len(optimal)-1,15)
	for i in range(0,max):
		orgIndex = optimal[i][0]
		newpal.append(pal[orgIndex])
		orgIndex+=16
		if orgIndex > 15:
			orgIndex = orgIndex - 16 + 128
		
		palstr= palstr+format(orgIndex, outputFormat)
		if i < max-1:
			palstr = palstr + ","
		else:
			palstr = palstr + "\""

	
	return palstr,newpal


pal = 0
outname = "output.png"
parser = argparse.ArgumentParser()
parser.add_argument("infile", help="the image to RLE encode")
parser.add_argument("-o", "--outfile", help="write resulting image to disk (default: output.png)")
parser.add_argument("-p", "--pal", type=int, help="the palette to use (0 = default, 1=secret, 2=best 16 colors from both)")
parser.add_argument("-c", "--compact", 	action='store_true',help="stores the RLE info in 2 chars per run, no comma")

args = parser.parse_args()

if args.pal:
	pal = args.pal
if args.outfile:
	outname = args.outfile
	if outname.find(".") == -1:
		# no extension given
		outname = outname +".png"
	basename=outname[:outname.rfind(".")]
else:
	basename=args.infile[:args.infile.rfind(".")]

if args.compact:
	compact = True
		
	
if pal < 0 or pal > 2:
	print("-p, --pal must be either 0 (normal pal), 1 (secret pal) or 2 (best 16 of both pals)")
	quit()

print("Encoding "+args.infile+" using pal "+str(pal) + " to "+outname)

im = Image.open(args.infile)
getcolors(im,pals[pal])
if pal == 2:
	cnt = 0
	for i in range(0,32):
		if counts[i]:
			#print(i, counts[i])
			bestcolor.append( (i, counts[i]) )
			cnt = cnt +1
	palstr, finalpal = createpal(bestcolor, pals[pal])
	getcolors(im,finalpal)

im.save(outname, "PNG")

if pal == 2:
	print(basename +"_pal=" + palstr)

rleStr=rle()
print("-- " +args.infile + " rle endcoded charcount:"+ str(len(rleStr)))
print(basename +"_rle=" + rleStr)
