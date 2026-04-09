#!/usr/bin/env python3
import rospy
import math
import sys
sys.path.append("/home/ubuntu/catkin_ws/src/mecanum_robot/scripts")
from geometry_msgs.msg import Twist, Quaternion, TransformStamped
from nav_msgs.msg import Odometry
from roboclaw_3 import Roboclaw
from tf2_ros import TransformBroadcaster
from tf.transformations import quaternion_from_euler

class MecanumController:
    def __init__(self):
        rospy.init_node('mecanum_controller')
        
        # 1. Parámetros físicos del robot
        self.wheel_diameter = 0.152  # 15.2 cm
        self.wheel_radius = self.wheel_diameter / 2.0
        self.L = 0.125  # 12.5 cm (semidistancia longitudinal)
        self.w = 0.285  # 28.5 cm (semidistancia transversal)
        
        # 2. Configuración del motor (valores del ejemplo básico)
        self.encoder_ppr_motor = 500  # PPR en el eje del motor
        self.gear_ratio = 18          # Relación de reducción 1:18
        self.motor_max_rpm = 175      # RPM en el eje del motor
        
        # 3. Cálculos derivados (para odometría)
        self.encoder_ppr_wheel = self.encoder_ppr_motor * self.gear_ratio  # 9000 PPR
        self.wheel_circumference = math.pi * self.wheel_diameter
        self.meters_per_tick = self.wheel_circumference / self.encoder_ppr_wheel  # ≈ 5.3e-5 m/tick
        
        # 4. Configuración RoboClaw (verifica el puerto adecuado, aquí se usa ttyAMA0)
        self.addresses = [0x80, 0x81, 0x83, 0x82]  # [FL, FR, RL, RR]
        self.rc = Roboclaw("/dev/ttyAMA0", 115200)
        self.rc.Open()
        
        # 5. Variables de estado para odometría
        self.x = 0.0        # Posición X (metros)
        self.y = 0.0        # Posición Y (metros)
        self.theta = 0.0    # Orientación (radianes)
        self.last_encoders = [0, 0, 0, 0]
        self.last_time = rospy.Time.now()
        
        # 6. Variables para comandos de velocidad
        self.current_twist = Twist()
        
        # Factor de aceleración y escala (basado en tu ejemplo básico)
        self.acceleration = 70000  
        self.scale_factor = 40000 / 0.07  # ≈571428, de modo que 0.07 m/s se convierta en 40000 ticks
        
        # 7. Configuración ROS
        self.odom_pub = rospy.Publisher('/odom', Odometry, queue_size=10)
        self.tf_broadcaster = TransformBroadcaster()
        rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback)
        
        # 8. Seguridad: detener motores al apagarse el nodo
        rospy.on_shutdown(self.stop_motors)

    def cmd_vel_callback(self, msg):
        """Almacena el último comando Twist recibido."""
        self.current_twist = msg

    def send_motor_commands(self):
        """
        Convierte el último Twist en comandos para cada rueda usando la cinemática inversa.
        Se utiliza SpeedAccelM1 con un valor de aceleración fijo para lograr cambios suaves.
        """
        vx = self.current_twist.linear.x    # m/s
        vy = self.current_twist.linear.y    # m/s
        wz = self.current_twist.angular.z   # rad/s
        
        # Cinemática inversa para mecanum (orden: FL, FR, RL, RR)
        factor = (self.L + self.w) * wz
        wheel_speeds_mps = [
            vx - vy - factor,  # Rueda frontal izquierda (0x80)
            vx + vy + factor,  # Rueda frontal derecha (0x81)
            vx + vy - factor,  # Rueda trasera izquierda (0x83)
            vx - vy + factor   # Rueda trasera derecha (0x82)
        ]
        
        # Convertir velocidades (m/s) a ticks usando el factor de escala
        wheel_ticks = [int(speed * self.scale_factor) for speed in wheel_speeds_mps]
        
        # Enviar comandos a cada motor con aceleración
        for addr, ticks in zip(self.addresses, wheel_ticks):
            self.rc.SpeedAccelM1(addr, self.acceleration, ticks)

    def read_encoders(self):
        """Lee los valores actuales de los encoders."""
        return [self.rc.ReadEncM1(addr)[1] for addr in self.addresses]

    def update_odometry(self):
        """Actualiza la posición usando cinemática directa."""
        now = rospy.Time.now()
        dt = (now - self.last_time).to_sec()
        if dt == 0:
            return
        current_encoders = self.read_encoders()
        
        # Calcular desplazamiento en ticks
        delta_ticks = [cur - last for cur, last in zip(current_encoders, self.last_encoders)]
        self.last_encoders = current_encoders
        
        # Convertir ticks a metros
        delta_meters = [ticks * self.meters_per_tick for ticks in delta_ticks]
        
        # Cinemática directa (promediando contribuciones de las 4 ruedas)
        vx = sum(delta_meters) / (4 * dt)
        vy = (-delta_meters[0] + delta_meters[1] + delta_meters[2] - delta_meters[3]) / (4 * dt)
        wz = (-delta_meters[0] + delta_meters[1] - delta_meters[2] + delta_meters[3]) / (4 * (self.L + self.w) * dt)
        
        # Integrar para obtener posición
        self.x += vx * dt
        self.y += vy * dt
        self.theta += wz * dt
        
        # Normalizar ángulo entre [-π, π]
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
        self.last_time = now

    def publish_odometry(self):
        """Publica la odometría y la transformada TF."""
        odom = Odometry()
        odom.header.stamp = rospy.Time.now()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"
        
        # Posición y orientación
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        q = quaternion_from_euler(0, 0, self.theta)
        odom.pose.pose.orientation = Quaternion(*q)
        
        # Covarianza (valor indicativo)
        odom.pose.covariance = [0.01]*36
        
        self.odom_pub.publish(odom)
        
        # Publicar transformada TF
        transform = TransformStamped()
        transform.header.stamp = odom.header.stamp
        transform.header.frame_id = "odom"
        transform.child_frame_id = "base_link"
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.rotation = odom.pose.pose.orientation
        self.tf_broadcaster.sendTransform(transform)

    def stop_motors(self):
        """Detiene todos los motores."""
        for addr in self.addresses:
            self.rc.SpeedM1(addr, 0)

    def run(self):
        # Ciclo principal a 50 Hz para mayor reactividad
        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            self.send_motor_commands()
            self.update_odometry()
            self.publish_odometry()
            rate.sleep()

if __name__ == '__main__':
    try:
        controller = MecanumController()
        controller.run()
    except rospy.ROSInterruptException:
        controller.stop_motors()

