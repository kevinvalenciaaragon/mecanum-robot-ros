import time
from roboclaw_3 import Roboclaw

#Linux comport name
rc = Roboclaw("/dev/ttyS0",115200)
rc.Open()

a1=70000
vel=40000
fd=2
while(1):
        ch=input("ingresa una tecla ")
        if (ch == "8"):
                rc.SpeedAccelM1(0x80,a1,vel)
                rc.SpeedAccelM1(0x81,a1,vel)
                rc.SpeedAccelM1(0X83,a1,vel+100)
                rc.SpeedAccelM1(0x82,a1,vel)
                print ("adelante")
        if (ch == "2"):
                rc.SpeedAccelM1(0x80,a1,-vel)
                rc.SpeedAccelM1(0x81,a1,-vel)
                rc.SpeedAccelM1(0X83,a1,-vel)
                rc.SpeedAccelM1(0x82,a1,-vel)
                print ("atras")
        if (ch == "4"):
                rc.SpeedAccelM1(0x80,a1,-vel)
                rc.SpeedAccelM1(0x81,a1,vel)
                rc.SpeedAccelM1(0X83,a1,vel)
                rc.SpeedAccelM1(0x82,a1,-vel)
        if (ch == "6"):
                rc.SpeedAccelM1(0x80,a1,vel-2000)
                rc.SpeedAccelM1(0x81,a1,-vel)
                rc.SpeedAccelM1(0X83,a1,-vel-2000)
                rc.SpeedAccelM1(0x82,a1,vel)
        if (ch == "9"):
                rc.SpeedAccelM1(0x80,a1,vel)
                rc.SpeedAccelM1(0x81,a1,vel/fd)
                rc.SpeedAccelM1(0X83,a1,vel/fd)
                rc.SpeedAccelM1(0x82,a1,vel)
        if (ch == "7"):
                rc.SpeedAccelM1(0x80,a1,vel/fd)
                rc.SpeedAccelM1(0x81,a1,vel)
                rc.SpeedAccelM1(0X83,a1,vel)
                rc.SpeedAccelM1(0x82,a1,(vel/fd))
        if (ch == "1"):
                rc.SpeedAccelM1(0x80,a1,-vel/fd)
                rc.SpeedAccelM1(0x81,a1,-vel)
                rc.SpeedAccelM1(0X83,a1,-vel)
                rc.SpeedAccelM1(0x82,a1,-vel/fd)
        if (ch == "3"):
                rc.SpeedAccelM1(0x80,a1,-vel)
                rc.SpeedAccelM1(0x81,a1,-vel/fd)
                rc.SpeedAccelM1(0X83,a1,-vel/fd)
                rc.SpeedAccelM1(0x82,a1,-vel)
        if (ch == "5"):
                rc.SpeedAccelM1(0x80,a1+5000,0)
                rc.SpeedAccelM1(0x81,a1+5000,0)
                rc.SpeedAccelM1(0X83,a1+5000,0)
                rc.SpeedAccelM1(0x82,a1+5000,0)
        if (ch == "."):
                rc.SpeedAccelM1(0x80,a1,vel)
                rc.SpeedAccelM1(0x81,a1,-vel/fd)
                rc.SpeedAccelM1(0X83,a1,vel)
                rc.SpeedAccelM1(0x82,a1,-vel/fd)
        if (ch == "0"):
                rc.SpeedAccelM1(0x80,a1,-vel/fd)
                rc.SpeedAccelM1(0x81,a1,vel)
                rc.SpeedAccelM1(0X83,a1,-vel/fd)
                rc.SpeedAccelM1(0x82,a1,vel)

        if (ch == "q"):
                break
        if (ch == "+"):
                vel=vel+5000
                print ('la velocidad es: '+str(vel))
        if (ch=="-"):
                vel=vel-5000
                print ('la velocidad es: '+str(vel))

