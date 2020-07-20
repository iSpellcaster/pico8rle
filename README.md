# pico8rle
An simple rle encoder for pic08.
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

## Limitations
Expects a 128x128 image. Other image sizes not supported at the moment.
But... I'm working on it.
  
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

function base64encode(val)
 local res,cur,i="", val
 while cur > 0 do
  i=cur%64
  res=sub(base64str,i+1,i+1)..res
  cur=flr(cur/64)
 end 	
 return res
end


function draw_rle(table,_x,_y, trans)
 local x,y,i,col,rle=0,0,1,0,0
 while i <= #table do
  col = shr(table[i] & 0xff00,8)--% 16		
  rle = table[i] & 0xff
  i+=1
  if not trans or (trans and col >0) then
   --rectfill is slightly faster
   --line(x+_x,_y+y,_x+x+rle,_y+y,col)
   rectfill(x+_x,_y+y,_x+x+rle,_y+y,col)
  end
  x+=rle
  if x >=128 then
   x = 0
   y += 1
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
