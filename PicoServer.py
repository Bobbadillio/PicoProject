import network
import socket
import time
from utime import sleep
import random
from neopixel import NeoPixel

NEOPIXEL_PIN = 0
NUMBER_PIXELS = 256
strip = NeoPixel(machine.Pin(NEOPIXEL_PIN), NUMBER_PIXELS)

ssid = 'pi wifi'
password = 'wifipassword'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)



def make_html():
    checkboxes = [f'<input type="checkbox" id="{i}" name="{i}" value="1">' for i in range(NUMBER_PIXELS)]
    boxes_per_row = 16
    row_checkboxes = ["".join(checkboxes[i:i+boxes_per_row]) for i in range(0,NUMBER_PIXELS,boxes_per_row)]
    final_checkboxes = "<div>" + "</div>\n<div>".join(row_checkboxes) + "</div>"
    final_html = ("""<!DOCTYPE html>
    <html>
        <head> <title>Pico W</title> </head>
        <body> <h1>Pico W</h1>
            <form method="post">"""
            
        + final_checkboxes
        +"""
                <input type="submit" name="submit" value="Submit">
            </form>
             <form method="get">
                <input type="submit" value="Run" />
            </form>
        </body>
    </html>
    """)
    print(f"final length is: {len(final_checkboxes)}")
    return final_html
html = make_html()

def allOff(strip, grid):
    for i in range(16):
        for j in range(16):
            grid[i][j] = OFF
            
    for each_index in range(256):
        strip[each_index] = (
            0,
            0,
            0
        )
    strip.write()
    

def randomlyLight(strip):
    for each_index in range(256):
        strip[each_index] = (
            random.randint(0,255),
            random.randint(0,255),
            random.randint(0,255)
            )
    strip.write()

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('listening on', addr)
ROWS=16
COLS=16



OFF=0
ON=1
life_grid = [[OFF for _ in range(16)] for _ in range(16)]

def write_pixel(x, y, value,strip):
    if y >= 0 and y < ROWS and x >=0 and x < COLS:
        # odd count rows 1, 3, 5 the wire goes from bottup
        if x % 2: 
            strip[(x+1)*ROWS - y - 1] = value             
        else: # even count rows, 0, 2, 4 the wire goes from the top down up
            strip[x*ROWS + y] = value
            
def write_index(pixel,strip,grid):
    x= pixel%16
    y= pixel//16
    grid[x][y] = ON
    write_pixel(x,y,(32,32,32),strip)


def conway_update(grid, N, strip): 
    # copy grid since we require 8 neighbors
    # for calculation and we go line by line
    print("copying grid")
    newGrid = [row.copy() for row in grid]
    print("grid copied")
    for i in range(N):
        for j in range(N):
            print(grid[i][j], end=" ")
        print()
    for i in range(N):
        for j in range(N):
 
            # compute 8-neighbor sum
            # using toroidal boundary conditions - x and y wrap around
            # so that the simulation takes place on a toroidal surface.
            total = (    grid[i      ][(j-1)%N ] + grid[i      ][(j+1)%N ] +
                         grid[(i-1)%N][ j      ] + grid[(i+1)%N][ j      ] +
                         grid[(i-1)%N][ (j-1)%N] + grid[(i-1)%N][ (j+1)%N] +
                         grid[(i+1)%N][ (j-1)%N] + grid[(i+1)%N][ (j+1)%N])
# row with col +/-
# col with row +/-
# row- with col +/-
# row+ with col +/-
            # apply Conway's rules
            if grid[i][ j]  == ON:
                if (total < 2) or (total > 3):
                    print(f"""pixel {(i, j)} currently {grid[i][j]} turns OFF total {total}, neighbors {(grid[i      ][(j-1)%N ], grid[i      ][(j+1)%N ] ,
                         grid[(i-1)%N][ j      ] , grid[(i+1)%N][ j      ] ,
                         grid[(i-1)%N][ (j-1)%N] , grid[(i-1)%N][ (j+1)%N] ,
                         grid[(i+1)%N][ (j-1)%N] , grid[(i+1)%N][ (j+1)%N])}""")
                    newGrid[i][j] = OFF
                    write_pixel(i,j, (0,0,0), strip)
            else:
                if total == 3:
                    print(f"""pixel {(i, j)} currently {grid[i][j]} turns ON total {total}, neighbors {(grid[i      ][(j-1)%N ] , grid[i      ][(j+1)%N ] ,
                         grid[(i-1)%N][ j      ] , grid[(i+1)%N][ j      ] ,
                         grid[(i-1)%N][ (j-1)%N] , grid[(i-1)%N][ (j+1)%N] ,
                         grid[(i+1)%N][ (j-1)%N] , grid[(i+1)%N][ (j+1)%N])}""")
                    newGrid[i][j] = ON
                    write_pixel(i,j, (32,32,32),strip)
 
    # update data
    grid[:] = newGrid[:]
    strip.write()

# Listen for connections
stateis = "LED is UNKNOWN"


while True:
    try:
        cl, addr = s.accept()
        print('\nclient connected from', addr)
        request = cl.recv(1024)
        #print(request)

        request_parts = str(request)[:].split("\\r\\n")[-1].split("&")
        print(f"req start: {str(request[:16])}")
        if request[:4] == b"POST":
            allOff(strip, life_grid)
            
            for each_val in request_parts:
                settings = each_val.split("=")
                if len(settings)!=2:
                    continue
                left = settings[0].strip()
                if str.isdigit(left):
                    print(f"selected: {int(left)}")
                    write_index(int(left),strip,life_grid)
                    #strip[int(left)] = (12,12,12)
            strip.write()
                    
            print(f"\nREQUEST PARTS: \n {request_parts}\n")
        elif request[:3] == b"GET":
            print("RUNNING")
            for i in range(100):
                conway_update(life_grid, 16, strip) 
                sleep(.5)
                print(f"iter {i}")
            print("DONE")
        
        response = html

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.sendall(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')