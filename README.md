# pico8rle

This tool allows you to convert images to be used in pico8 w/o eating up additional sprite memory.
It basically stores an image as a string. To create this string a python script is used.

The python code works like this
- map the image to the pico8 palette (either the normal, secret, or the 16 closest from both, your choice)
- It then converts it into horizontal lines, stored as `col C for N number of pixels`. This is also where the name comes from. RLE stands for "run length encoding". It works best if you have large blocks (well, lines) of a single color. It will work horribly with dithered images.
- this informtaion is stored in a string in a really basic way. The only "clever" thing here is, that I used a base64 encode, to keep the resulting size somewhat down.
- You can copy&paste this string into your pico8 project, and display the image using the functions given below. Either as background image, or with transparency for index 0. 

![alt text](https://github.com/iSpellcaster/pico8rle/raw/master/rle%20p8_2.gif "Short demo of the code")
![alt text](https://github.com/iSpellcaster/pico8rle/raw/master/rle%20p8_1.gif "Short demo of the code")


So, it's *a simple rle encoder for pico8.*

## Dependencies

It uses Pillow (https://pillow.readthedocs.io/en/stable/) for image I/O, so make sure to install pillow. See: https://pillow.readthedocs.io/en/stable/installation.html

## Usage
```
usage: rle_encode.py [-h] [-o OUTFILE] [-p PAL] infile

positional arguments:
  infile                the image to RLE encode

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        write resulting image to disk (default: output.png)
  -p PAL, --pal PAL     the palette to use (0 = default, 1=secret, 2=best 16 colors from both)
  -c, --compact         stores the RLE info in 2 chars per run, no comma
  ```
  
Running the script will output the data needed to use in pico8 on stdout.
This includes a rle string for the image and a palette str (if `--pal 2` is used)

## Base64 encoding
There's a new parameter -c/ --compact which stores the rle data in a base64 format.
You can explode these using the explode64 function below. This reduces the length of most runs from 4 characters (including the separator comma) to 2 chars.

Here're some values to compare:
 - Antiriad title, hexencoded with commas (default): 8467 characters
 - Antiriad title, base64 encoded, without commas (-c): 4852 characters
 
So I'd suggest that you use the -c/--compact switch and the explode64() function.

## Variable image size
The tool will now encode images up to 255x255.
This also means that I had to add the image dimensions to the RLE output. Which gives you the benefit that the first to alues in your table will be the width and height of the encoded image.
```
sprite = explode64(sprite_rle)
spr_width = sprite[1]
spr_height = sprite[2]
```

I also added a spr_rle_flip() function to render a mirrored version of the image. Besides sprites, you could use this o count down on size of symmetric scenes.
The actual code is not blazingly fast, but you should be able to use it for a couple of rather large sprites w/o too much trouble.


## Example calls of the tool
```
pico8rle.py -p 0 -c kanji.png
```
Encodes `kanji.png` in base64 encoding, using the standard pico8 palette.
```
pico8rle.py -p 1 -c antiriad.png
```
Encodes `antiriad.png` in base64 encoding, using the secret pico8 palette.
```
pico8rle.py -p 2 -c batman.png
```
Emcodes `batman.png` in base64 encoding, using the 16 best fitting colors from the standard and secret pico8 palette.
In this case, you'll also get a palette string you can use to set this palette using `setpal' (see below).

## Using it in your own project
To run the script, you'll need python (v3.x) installed on your machine and the Pillow image library for python. Links can be found above.
To sue the encoded images, you can copy&paste the functions given below into your own code, 

While you could expldoe the images in your _draw() function, I'd recommend that you explode them once, and only call the draw_rle(), spr_rle() and spr_rle_flipped() in your actual drawing code.


You can find an example cartridge on the pico8 BBs: https://www.lexaloffle.com/bbs/?tid=38887
I've also uploaded this cart into this repo:
![alt text](https://github.com/iSpellcaster/pico8rle/raw/master/rle.p8.png "Short demo of the code")


  
## pico8 functions to use the output
Use the following methods to use the encoded image
```
base64str='0123456789abcdefghijklmnopqrstuvwxyz!@#$%^&*()_-+=[]}{;:<>,./?~|'

function explode_hex(s, delimiter)
 local retval,i=split(s,delimiter,false)
  
 for i=1,#retval do
  retval[i] =("0x"..retval[i])+0
 end
 return retval
end


function explode64(s)
 local retval,lastpos,i = {},1,2
 
 while i <= #s do
  add(retval,base64decode(sub(s, lastpos, i)))
  
  lastpos = i+1
  i += 2
 end
 return retval
end


function base64decode(str)
 val=0
 for i=1,#str do
  c=sub(str,i,i)
  for a=1,#base64str do
   v=sub(base64str,a,a)
   if c==v then
    val *= 64
    val += a-1
    break
   end
  end
 end
 return val
end

-- chances are, you'll never use this function
-- and it's not required by any of the other functions
-- so, feel free to delete it :)
function base64encode(val)
 local res,cur,i="", val
 while cur > 0 do
  i=cur%64
  res=sub(base64str,i+1,i+1)..res
  cur=flr(cur/64)
 end 	
 return res
end

function spr_rle(table,_x,_y)
 local x,y,i,col,rle,w=0,0,3,0,0,table[1]
 while i <= #table do
  col = shr(table[i] & 0xff00,8)--% 16		
  rle = table[i] & 0xff
  i+=1
  if col!=0 then
   --rectfill is slightly faster
   --line(x+_x,_y+y,_x+x+rle,_y+y,col)
   rectfill(x+_x,y+_y,x+_x+rle-1,_y+y,col)
  end
  x+=rle
  if x >=w then
   x = 0
   y += 1
  end
 end
end

function spr_rle_flip(table,_x,_y)
 local x,y,i,col,rle,w=0,0,3,0,0,table[1]
 _x+=w
  while i <= #table do
  col = shr(table[i] & 0xff00,8)--% 16		
  rle = table[i] & 0xff
  i+=1
  if col!=0 then
   --rectfill is slightly faster
   --line(x+_x,_y+y,_x+x+rle,_y+y,col)
   rectfill(_x-x-rle+1,y+_y,_x-x,_y+y,col)
  end
  x+=rle
  if x >=w then
   x = 0
   y += 1
  end
 end
end


function draw_rle(table,_x,_y)
 local x,y,i,col,rle,w=0,0,3,0,0,table[1]

 while i <= #table do
  col = shr(table[i] & 0xff00,8)--% 16		
  rle = table[i] & 0xff
  i+=1
  --rectfill is slightly faster
  --line(x+_x,_y+y,_x+x+rle,_y+y,col)
  rectfill(x+_x,y+_y,x+_x+rle-1,_y+y,col)

  x+=rle
  if x >=w then
   x = 0
   y +=1
  end
 end
end

function setpal(palstr)
 local i,palindex
 palindex=explode_hex(palstr,",")
 for i=1,#palindex do
  pal(i-1,palindex[i],1)
 end
end

-- set "secret" palette
function pal2()
 local i
 for i=0,15 do
  pal(i,128+i,1)
 end
end


function cprint(txt,x,y,cols)
 local len,org=#txt*4+4,clip() 
 local a
 x=x and x or 64-len/2
 for a=1,3 do
  print(txt,x,y,cols[a])    
  clip(x,y+a*2,len,2)
 end
 clip(org)
end
```
