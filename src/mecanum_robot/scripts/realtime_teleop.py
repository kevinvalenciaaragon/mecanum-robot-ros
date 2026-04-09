##!/usr/bin/env python3
import rospy
import sys
import select
import tty
import termios
from geometry_msgs.msg import Twist

class RealtimeTeleop:
    def __init__(self):
        rospy.init_node('realtime_teleop')
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.twist = Twist()
        
        # Parámetros de velocidad
        self.linear_speed = 0.07  # m/s (ajuste según pruebas)
        self.angular_speed = 0.5  # rad/s
        self.speed_step = 0.01    # Incremento/decremento de velocidad
        
        # Configurar terminal para lectura sin bloqueo
        self.settings = termios.tcgetattr(sys.stdin)
        
        print("\nCONTROLES EN TIEMPO REAL:")
        print("  W/A/S/D : Movimiento continuo (suelta para detener)")
        print("  Q/E     : Rotación continua")
        print("  +/-     : Ajustar velocidad")
        print("  CTRL+C  : Salir")
        
        # Variables para controlar el timeout de la tecla
        self.last_key_time = rospy.Time.now()
        self.key_timeout = 0.5  # Si no se recibe tecla en 0.5 seg, se detiene

    def get_key(self, timeout=0.05):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def run(self):
        rate = rospy.Rate(20)  # Controla el bucle a 20 Hz para mayor reactividad
        while not rospy.is_shutdown():
            key = self.get_key().lower()
            current_time = rospy.Time.now()
            
            # Actualiza el tiempo del último comando recibido si se detecta una tecla
            if key != '':
                self.last_key_time = current_time

            # Si ha pasado más tiempo que el timeout, se detiene el robot
            if (current_time - self.last_key_time).to_sec() > self.key_timeout:
                self.twist.linear.x = 0.0
                self.twist.linear.y = 0.0
                self.twist.angular.z = 0.0
            else:
                # Actualiza el comando según la tecla presionada
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
                    self.linear_speed = min(0.1, self.linear_speed + self.speed_step)
                    print(f"Velocidad lineal actual: {self.linear_speed:.2f} m/s")
                elif key == '-':
                    self.linear_speed = max(0.01, self.linear_speed - self.speed_step)
                    print(f"Velocidad lineal actual: {self.linear_speed:.2f} m/s")
                # Si se presiona cualquier otra tecla o no se detecta ninguna, se mantiene el último comando

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
from select import select
from geometry_msgs.msg import Twist

class RealtimeTeleop:
    def __init__(self):
        rospy.init_node('mecanum_teleop')
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.twist = Twist()
        
        # Parámetros de control
        self.linear_speed = 0.5   # m/s
        self.angular_speed = 1.0  # rad/s
        self.speed_step = 0.1
        
        # Configurar terminal
        self.settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        
        print("""Control del Robot Mecanum:
        W/S: Adelante/Atrás
        A/D: Izquierda/Derecha
        Q/E: Rotación
        +/-: Ajustar velocidad
        SPACE: Detener
        Ctrl+C: Salir""")

    def get_key(self):
        """Lectura no bloqueante de teclas"""
        return sys.stdin.read(1) if select([sys.stdin], [], [], 0)[0] else ''

    def run(self):
        try:
            while not rospy.is_shutdown():
                key = self.get_key().lower()
                
                # Resetear comandos
                self.twist.linear.x = 0.0
                self.twist.linear.y = 0.0
                self.twist.angular.z = 0.0
                
                # Mapeo de teclas
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
                    self.linear_speed = min(2.0, self.linear_speed + self.speed_step)
                    print(f"Velocidad actual: {self.linear_speed} m/s")
                elif key == '-':
                    self.linear_speed = max(0.1, self.linear_speed - self.speed_step)
                    print(f"Velocidad actual: {self.linear_speed} m/s")
                elif key == ' ':
                    pass  # Velocidad ya está en cero
                
                self.pub.publish(self.twist)
                
        finally:
            # Restaurar configuración del terminal
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            # Detener motores al salir
            self.twist = Twist()
            self.pub.publish(self.twist)

if __name__ == '__main__':
    try:
        teleop = RealtimeTeleop()
        teleop.run()
    except rospy.ROSInterruptException:
        pass
