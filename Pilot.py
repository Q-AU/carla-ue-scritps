import carla
import random
import sys
import signal
import time
from functools import partial
import socket
import math
import keyboard  

SENSOR_SEND_IP = "127.0.0.1"
RGB_SEND_START_PORT = 2337


socketsByPort = {}

socketType = socket.AF_INET
protocolType = socket.SOCK_STREAM

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((IMAGE_SEND_IP,IMAGE_SEND_PORT))

def attach_sensor(world, vehicle, transform, sensorCallback, sensorType):
    cam_bp = world.get_blueprint_library().find(sensorType)
    cam_bp.set_attribute("image_size_x", str(1920))
    cam_bp.set_attribute("image_size_y", str(1080))
    cam_bp.set_attribute("fov",str(45))
    cam = world.spawn_actor(cam_bp, transform, attach_to = vehicle, attachment_type = carla.AttachmentType.Rigid)
    cam.listen(sensorCallback)
    return cam

attach_rgb_camera = partial(attach_sensor, sensorType = 'sensor.camera.rgb')



def rgb_callback(image, port):
    if port not in socketsByPort:
        try:
            sock = socket.socket(socketType, protocolType)
            socketsByPort[port] = sock
            sock.connect((SENSOR_SEND_IP, port))
            
        except ConnectionRefusedError:
            #print("connection refused error")
            del socketsByPort[port]
            return
        
    sock = socketsByPort[port]

    try:
        still_connected = send_image(image, sock)
    # image.save_to_disk("images/", carla.ColorConverter.CityScapesPalette)
        if not still_connected:
            del socketsByPort[port]
            sock.close()
    except ConnectionAbortedError:
        del socketsByPort[port]
        sock.close()
    
def send_image(image, sock):
    try:
        #print(len(image.raw_data))
        sock.sendall(image.raw_data)
        return True
    except ConnectionResetError:
        #print("connection reset error")
        return False
    
    return False

    

def main():
    try:
        ##Set all created actors in a list so they can be destroyed easily

        client = carla.Client('localhost',2000)
        client.set_timeout(10.0)

        world = client.get_world()
        spawns = world.get_map().get_spawn_points()
        randLocation = random.choice(spawns)
        bp  = world.get_blueprint_library().find("vehicle.tesla.model3")

        vehicle = world.try_spawn_actor(bp, randLocation)

        print(vehicle)
        print(bp)

        world.wait_for_tick()



        """Hardcoded setup for 5 cameras for wide-view 1 camera for rear view """
        ##Location controls (X=forward-backwards, Y=lef-right, Z=up-down)
        ##Rotation controls (X=up-down, Y=left-right,Z)

        cam_location=carla.Location(-0.15,-0.4,1.2)
        #cam_most_left_location = carla.Location(0.3,0,1.3)
        cam_most_left_rotation = carla.Rotation(0,-90,0)
        cam_most_left = attach_rgb_camera(world, vehicle, carla.Transform(cam_location,cam_most_left_rotation), 
            lambda image: partial(rgb_callback, port = RGB_SEND_START_PORT + 0)(image) )

        #cam_left_location = carla.Location(0.3,0,1.3)
        cam_left_rotation = carla.Rotation(0,-45,0)
        cam_left = attach_rgb_camera(world, vehicle, carla.Transform(cam_location,cam_left_rotation), 
            lambda image: partial(rgb_callback, port = RGB_SEND_START_PORT + 1)(image) )


        #cam_center_location = carla.Location(0.3,0,1.3)
        cam_center_rotation = carla.Rotation(0,0,0)
        cam_center = attach_rgb_camera(world, vehicle, carla.Transform(cam_location,cam_center_rotation), 
            lambda image: partial(rgb_callback, port = (RGB_SEND_START_PORT + 2))(image))
        
        #cam_right_location = carla.Location(0.3,0,1.3)
        cam_right_rotation = carla.Rotation(0,45,0)
        cam_right = attach_rgb_camera(world, vehicle, carla.Transform(cam_location,cam_right_rotation), 
            lambda image: partial(rgb_callback, port = (RGB_SEND_START_PORT + 3))(image))
        
        
        #cam_most_right_location = carla.Location(0.3,0,1.3)
        cam_most_right_rotation = carla.Rotation(0,90,0)
        cam_most_right = attach_rgb_camera(world, vehicle, carla.Transform(cam_location,cam_most_right_rotation), 
            lambda image: partial(rgb_callback, port = (RGB_SEND_START_PORT + 4))(image))
        
        #cam_rear_location = carla.Location(0.3,0,1.3)
        cam_rear_rotation = carla.Rotation(0,180,0)
        cam_rear = attach_rgb_camera(world, vehicle, carla.Transform(cam_location,cam_rear_rotation), 
            lambda image: partial(rgb_callback, port = (RGB_SEND_START_PORT + 5))(image))
    

        observer = world.get_spectator()
        observer.set_transform(cam_center.get_transform())

        """Autopilot"""        
        ##vehicle.set_autopilot(True)
        """Manual control, needs to be defined!!"""        

        # while True:  # making a loop
        #     try:  # used try so that if user pressed other than the given key error will not be shown
        #         if keyboard.is_pressed('q'):  # if key 'q' is pressed 
        #             vehicle.apply_control(carla.VehicleControl(throttle=1.0))
        #             print('You Pressed A Key!')
        #             break  # finishing the loop
        #     except:
        #         break  # if user pressed a key other than the given key the loop will break

    finally:
        #the following just prevents the app from closing immediately after start (with input(...), by waiting for user input), and the exception handler intercepts ctrl + c

        try:
            k = input("input: ") 
            ##Destroy cameras; for some reason if they are stored in an array the script doesnt work
            cam_left.destroy()
            cam_most_left.destroy()
            cam_center.destroy()
            cam_right.destroy()
            cam_most_right.destroy()
            cam_rear.destroy()
            ##Destroy vehicle
            vehicle.destroy()

            for sock in socketsByPort.values():
                sock.close()

            client.reload_world()

        except KeyboardInterrupt:
            print("exiting")
            
      
if __name__ == "__main__":
    main()