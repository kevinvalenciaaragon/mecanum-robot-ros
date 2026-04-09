#!/usr/bin/env python3
import rospy
import sys
import select
import tty
import termios
from geometry_msgs.msg import Twist

class RealtimeTeleop:
    def __init__(self):
        rospy.init_node('realtime_teleop')
        self.pub = rospy.Publisher('/cmd_vel_teleop', Twist, queue_size=1)
        self.twist = Twist()
        
        # Parámetros de velocidad
        self.linear_speed = 0.07   # Velocidad lineal inicial (m/s)
        self.angular_speed = 0.5   # Velocidad angular inicial (rad/s)
        self.speed_step = 0.01     # Incremento/decremento de velocidad lineal
        self.angular_step = 0.1    # Incremento/decremento de velocidad angular
        
        # Configurar terminal para lectura sin bloqueo
        self.settings = termios.tcgetattr(sys.stdin)

        print("\nCONTROLES EN TIEMPO REAL:")
        print("  W/S : Adelante / Atrás")
        print("  A/D : Izquierda / Derecha")
        print("  Q/E : Rotación Izq / Der")
        print("  +/- : Ajustar velocidad lineal")
        print("  ./0 : Ajustar velocidad angular")
        print("  CTRL+C  : Salir")

        # Variables para controlar el timeout de la tecla
        self.last_key_time = rospy.Time.now()
        self.key_timeout = 0.5  # Si no se recibe tecla en 0.5 seg, se detiene

    def get_key(self, timeout=0.05):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        key = sys.stdin.read(1) if rlist else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def run(self):
        rate = rospy.Rate(20)  # Controla el bucle a 20 Hz para mayor reactividad
        while not rospy.is_shutdown():
            key = self.get_key().lower()
            current_time = rospy.Time.now()
            
            # Si se recibe una tecla, actualizar el tiempo del último comando
            if key:
                self.last_key_time = current_time

            # Si ha pasado más tiempo que el timeout, se detiene el robot
            if (current_time - self.last_key_time).to_sec() > self.key_timeout:
                self.twist.linear.x = 0.0
                self.twist.linear.y = 0.0
                self.twist.angular.z = 0.0
            else:
                # Actualiza los comandos según la tecla presionada
                if key == 'w':
                    self.twist.linear.x = self.linear_speed
                elif key == 's':
                    self.twist.linear.x = -self.linear_speed
                elif key == 'a':
                    self.twist.linear.y = self.linear_speed
                elif key == 'd':
                    self.twist.linear.y = -self.linear_speed
                elif key == 'q':
                    self.twist.angular.z = self.angular_speed
                elif key == 'e':
                    self.twist.angular.z = -self.angular_speed
                elif key == '+':
                    self.linear_speed = min(0.2, self.linear_speed + self.speed_step)
                    print(f"Velocidad lineal: {self.linear_speed:.2f} m/s")
                elif key == '-':
                    self.linear_speed = max(0.01, self.linear_speed - self.speed_step)
                    print(f"Velocidad lineal: {self.linear_speed:.2f} m/s")
                elif key == '.':
                    self.angular_speed = min(2.0, self.angular_speed + self.angular_step)
                    print(f"Velocidad angular: {self.angular_speed:.2f} rad/s")
                elif key == '0':
                    self.angular_speed = max(0.1, self.angular_speed - self.angular_step)
                    print(f"Velocidad angular: {self.angular_speed:.2f} rad/s")

            self.pub.publish(self.twist)
            rate.sleep()

        # Al salir, detener el robot y restaurar la configuración del terminal
        self.twist = Twist()
        self.pub.publish(self.twist)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        print("\nConexión cerrada. Motores detenidos.")

if __name__ == '__main__':
    try:
        node = RealtimeTeleop()
        node.run()
    except rospy.ROSInterruptException:
        pass

