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
  ```
  
Running the script will output the code needed to use in pico8 on stdout.
This includes a rle string for the image and a palette str (if `--pal 2` is used)
  
## pico8 functions to use the output
Use the following methods to use the encoded image
```
-- explode_hex
-- use this to convert the rle string into a table that can be
-- used with draw_rle
--
-- heaviliy based on splixel's
-- explode_internal function:
-- https://www.lexaloffle.com/bbs/?tid=28160
-- i changed the code to interpret the contents as hex values
function explode_hex(s, delimiter)
 local retval,lastpos,i = {},1,1
 
 for i=1,#s do
  if sub(s,i,i) == delimiter then
   add(retval, ("0x"..sub(s, lastpos, i-1))+0)
   i += 1
   lastpos = i
  end
 end
 return retval
end


-- draw_rle
-- draws a rle encoded image at _x, _y. 
-- if trans is set, palette index 0 will be used for transparency
function draw_rle(table,_x,_y, trans)
 local x,y,i,col,rle=0,0,1,0,0
	while i < #table do
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

-- setpal
-- takes a palette string exported from pico8rle
-- and sets the palette data accordingly
function setpal(palstr)
	local i,palindex
 palindex=explode_hex(palstr,",")
	for i=1,#palindex do
	 	pal(i-1,palindex[i],1)
	end
end

  ```
