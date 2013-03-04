# Build Directions #

Download / extract LCDProc source code

~~~
./configure --enable-drivers=hd44780
make server
cp server/drivers/hd44780.so /usr/lib/lcdproc
~~~

The driver was patched by Steve Whitcher <steve@whitcher.org> for use with the Sainsmart i2c Backpack.
