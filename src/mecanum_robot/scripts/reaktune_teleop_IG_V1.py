#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
import tkinter as tk

class TeleopGUI:
    def __init__(self, master):
        self.master = master
        master.title("Teleop Robot Controller")

        # Inicializar nodo ROS
        rospy.init_node("teleop_gui", anonymous=True)
        self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.twist = Twist()

        # Parámetros por defecto de velocidad
        self.linear_speed = 0.5    # m/s
        self.angular_speed = 1.0   # rad/s
        self.speed_step = 0.1      # Incremento/decremento para velocidad lineal
        self.angular_step = 0.1    # Incremento/decremento para velocidad angular

        # Crear la interfaz gráfica
        self.create_widgets()

        # Configurar bindings para teclado (presión y liberación)
        master.bind("<KeyPress>", self.on_key_press)
        master.bind("<KeyRelease>", self.on_key_release)

        # Para almacenar las teclas que están presionadas
        self.keys_pressed = set()

        # Publicar continuamente comandos Twist cada 50ms
        self.publish_loop()

    def create_widgets(self):
        # Frame para botones de movimiento (con teclado o click)
        move_frame = tk.Frame(self.master)
        move_frame.pack(pady=10)

        # Botón de avance
        self.btn_forward = tk.Button(move_frame, text="↑", command=self.move_forward, width=6, height=3)
        self.btn_forward.grid(row=0, column=1)

        # Botones laterales y de stop
        self.btn_left = tk.Button(move_frame, text="←", command=self.move_left, width=6, height=3)
        self.btn_left.grid(row=1, column=0)
        self.btn_stop = tk.Button(move_frame, text="Stop", command=self.stop_robot, width=6, height=3)
        self.btn_stop.grid(row=1, column=1)
        self.btn_right = tk.Button(move_frame, text="→", command=self.move_right, width=6, height=3)
        self.btn_right.grid(row=1, column=2)

        # Botón de retroceso
        self.btn_backward = tk.Button(move_frame, text="↓", command=self.move_backward, width=6, height=3)
        self.btn_backward.grid(row=2, column=1)

        # Frame para botones de rotación
        rot_frame = tk.Frame(self.master)
        rot_frame.pack(pady=10)
        self.btn_rotate_left = tk.Button(rot_frame, text="Rotate Left", command=self.rotate_left, width=12)
        self.btn_rotate_left.grid(row=0, column=0, padx=5)
        self.btn_rotate_right = tk.Button(rot_frame, text="Rotate Right", command=self.rotate_right, width=12)
        self.btn_rotate_right.grid(row=0, column=1, padx=5)

        # Frame para ajustar velocidades con escalas (sliders)
        speed_frame = tk.Frame(self.master)
        speed_frame.pack(pady=10)
        tk.Label(speed_frame, text="Linear Speed (m/s):").grid(row=0, column=0, sticky="w")
        self.linear_scale = tk.Scale(speed_frame, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL)
        self.linear_scale.set(self.linear_speed)
        self.linear_scale.grid(row=0, column=1)
        
        tk.Label(speed_frame, text="Angular Speed (rad/s):").grid(row=1, column=0, sticky="w")
        self.angular_scale = tk.Scale(speed_frame, from_=0.0, to=5.0, resolution=0.1, orient=tk.HORIZONTAL)
        self.angular_scale.set(self.angular_speed)
        self.angular_scale.grid(row=1, column=1)

        # Instrucciones en la interfaz para el teclado
        instruct = ("Controles por teclado:\n"
                    "W/S: Avanzar/Retroceder\n"
                    "A/D: Desplazamiento lateral\n"
                    "Q/E: Rotar\n"
                    "+/-: Incrementar/Disminuir velocidad lineal\n"
                    "[/]: Disminuir velocidad angular\n"
                    "]: Incrementar velocidad angular")
        tk.Label(self.master, text=instruct).pack(pady=10)

    # Funciones para publicar Twist
    def publish_twist(self, linear_x=0.0, linear_y=0.0, angular_z=0.0):
        self.twist.linear.x = linear_x
        self.twist.linear.y = linear_y
        self.twist.angular.z = angular_z
        self.pub.publish(self.twist)

    # Funciones para los botones (acción directa al click)
    def move_forward(self):
        self.linear_speed = self.linear_scale.get()
        self.publish_twist(linear_x=self.linear_speed)

    def move_backward(self):
        self.linear_speed = self.linear_scale.get()
        self.publish_twist(linear_x=-self.linear_speed)

    def move_left(self):
        self.linear_speed = self.linear_scale.get()
        self.publish_twist(linear_y=self.linear_speed)

    def move_right(self):
        self.linear_speed = self.linear_scale.get()
        self.publish_twist(linear_y=-self.linear_speed)

    def rotate_left(self):
        self.angular_speed = self.angular_scale.get()
        self.publish_twist(angular_z=self.angular_speed)

    def rotate_right(self):
        self.angular_speed = self.angular_scale.get()
        self.publish_twist(angular_z=-self.angular_speed)

    def stop_robot(self):
        self.publish_twist(0.0, 0.0, 0.0)

    # Funciones para el manejo del teclado
    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        self.process_keys()

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
        self.process_keys()

    def process_keys(self):
        # Actualiza velocidades desde los sliders
        self.linear_speed = self.linear_scale.get()
        self.angular_speed = self.angular_scale.get()

        linear_x = 0.0
        linear_y = 0.0
        angular_z = 0.0

        # Movimiento lineal
        if 'w' in self.keys_pressed:
            linear_x += self.linear_speed
        if 's' in self.keys_pressed:
            linear_x -= self.linear_speed
        if 'a' in self.keys_pressed:
            linear_y += self.linear_speed
        if 'd' in self.keys_pressed:
            linear_y -= self.linear_speed

        # Rotación
        if 'q' in self.keys_pressed:
            angular_z += self.angular_speed
        if 'e' in self.keys_pressed:
            angular_z -= self.angular_speed

        # Ajuste de velocidades (lineal)
        if 'plus' in self.keys_pressed or 'equal' in self.keys_pressed:
            self.linear_speed = min(2.0, self.linear_speed + self.speed_step)
            self.linear_scale.set(self.linear_speed)
        if 'minus' in self.keys_pressed:
            self.linear_speed = max(0.0, self.linear_speed - self.speed_step)
            self.linear_scale.set(self.linear_speed)

        # Ajuste de velocidades (angular)
        if 'bracketleft' in self.keys_pressed:
            self.angular_speed = max(0.0, self.angular_speed - self.angular_step)
            self.angular_scale.set(self.angular_speed)
        if 'bracketright' in self.keys_pressed:
            self.angular_speed = min(5.0, self.angular_speed + self.angular_step)
            self.angular_scale.set(self.angular_speed)

        self.publish_twist(linear_x, linear_y, angular_z)

    # Función que publica periódicamente el mensaje Twist
    def publish_loop(self):
        self.pub.publish(self.twist)
        self.master.after(50, self.publish_loop)

def main():
    root = tk.Tk()
    gui = TeleopGUI(root)
    root.mainloop()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

