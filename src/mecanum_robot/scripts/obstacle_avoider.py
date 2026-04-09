#!/usr/bin/env python3
import rospy
import numpy as np
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleAvoider:
    def __init__(self):
        rospy.init_node('priority_obstacle_avoider')
        
        # Parámetros ajustables dinámicamente
        self.safety_distance = rospy.get_param('~safety_distance', 1)  # [m]
        self.max_linear_speed = rospy.get_param('~max_linear_speed', 0.2)  # [m/s]
        self.turning_speed = rospy.get_param('~turning_speed', 0.1)  # [rad/s]
        self.escape_angle = np.radians(rospy.get_param('~escape_angle', 45))  # [deg→rad]
        
        # Comunicación ROS
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        rospy.Subscriber('/scan', LaserScan, self.lidar_callback)
        rospy.Subscriber('/cmd_vel_teleop', Twist, self.teleop_callback)
        
        # Estado del sistema
        self.emergency_stop = False
        self.last_teleop_cmd = Twist()
        self.obstacle_direction = 0  # -1: izquierda, +1: derecha

        rospy.loginfo(f"Nodo iniciado con prioridad de seguridad: STO@ {self.safety_distance}m")

    def teleop_callback(self, msg):
        self.last_teleop_cmd = msg

    def lidar_callback(self, msg):
        ranges = np.array(msg.ranges)
        angle_inc = msg.angle_increment
        center_idx = len(ranges) // 2
        
        # Detección en cono frontal extendido
        scan_angle = int(self.escape_angle / angle_inc)
        frontal_scan = ranges[center_idx-scan_angle : center_idx+scan_angle]
        valid_ranges = frontal_scan[(frontal_scan > msg.range_min) & (frontal_scan < msg.range_max)]
        
        cmd_vel = Twist()
        
        if valid_ranges.size > 0:
            min_dist = np.min(valid_ranges)
            
            if min_dist < self.safety_distance:
                self.emergency_stop = True
                self._execute_escape_maneuver(cmd_vel, ranges, center_idx)
            else:
                self.emergency_stop = False
                cmd_vel = self._apply_speed_limits(self.last_teleop_cmd)
        else:
            cmd_vel = self.last_teleop_cmd
            self.emergency_stop = False
        
        self.cmd_vel_pub.publish(cmd_vel)

    def _execute_escape_maneuver(self, cmd_vel, ranges, center_idx):
        """Estrategia de escape: detención + giro hacia zona más libre"""
        # Análisis de espacios laterales
        left_region = ranges[:center_idx]
        right_region = ranges[center_idx:]
        
        left_clearance = np.mean(left_region[left_region < 3.0])  # 3m como rango práctico
        right_clearance = np.mean(right_region[right_region < 3.0])
        
        # Decisión de giro
        turn_direction = 1 if right_clearance > left_clearance else -1
        cmd_vel.angular.z = self.turning_speed * turn_direction
        
        # Log de emergencia
        rospy.logwarn(f"!EVASIÓN ACTIVADA! Giro {'derecha' if turn_direction>0 else 'izquierda'}")

    def _apply_speed_limits(self, cmd):
        """Asegura que la teleoperación no exceda límites seguros"""
        cmd.linear.x = np.clip(cmd.linear.x, -self.max_linear_speed, self.max_linear_speed)
        cmd.angular.z = np.clip(cmd.angular.z, -self.turning_speed, self.turning_speed)
        return cmd

if __name__ == '__main__':
    try:
        avoider = ObstacleAvoider()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
