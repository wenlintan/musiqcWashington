
from math import pi, atan, sin, cos, copysign

from flags import *
from simulation import *

class Car( Component ):
	def __init__( self ):
		super( Car, self ).__init__( ComponentType.Car )
		self.mass = 1500
		self.drag_coefficient = 0.4257
		self.brake_torque = 3000
		self.torque_points = [
			(1000, 400), (2000, 425), (3000, 450), (4000, 480),
			(5000, 470), (5800, 390)
			]

		self.cg_height = 0.5
		self.cg_to_front_axle = 1.
		self.cg_to_rear_axle = 1.

		self.differential_ratio = 3.42
		self.gears = [ 2.66, 1.78, 1.3, 1., 0.74 ]
		
		self.wheel_mass = 75
		self.wheel_radius = 0.33
		self.wheel_rotational_inertia = 0.5 * self.wheel_mass * \
			self.wheel_radius ** 2

		self.wheel_rolling_resistance = 12.8

		self.gear = 0
		self.acceleration = 0.
		self.braking = 0.
		self.steering_angle = 0.
		self.wheel_angular_velocity = 0.

	def torque( self, rpm ):
		if rpm < self.torque_points[0][0]:		
			self.gear -= 1
			self.gear = max( 0, self.gear )
			rpm = self.torque_points[0][0]
		if rpm > self.torque_points[-1][0]:
			self.gear += 1
			self.gear = min( len(self.gears)-1, self.gear )
			rpm = self.torque_points[-1][0]

		tpt = iter( self.torque_points )

		prev = next( tpt )
		curr = next( tpt )
		while( curr[0] < rpm ):
			prev, curr = curr, next( tpt )

		dr = curr[0] - prev[0]
		return prev[1] * (rpm - prev[0]) / dr + curr[1] * (curr[0] - rpm) / dr	

	def normalized_slip_ratio_force( self, slip_ratio ):
		return max( -1.2, min( 1.2, 1.2 / 0.05 * slip_ratio ) )

	def normalized_slip_angle_force( self, slip_angle ):
		return max( -1.1, min( 1.1, 1.1 / 0.05 * slip_angle ) )

	
from time import time
class CarSystem( System ):
	gravity = 9.8
	def __init__( self ):
		super( CarSystem, self ).__init__()
		
	last_time = time()
	def update( self, ent ):
		if not ent.has_component( ComponentType.Car ):
			return

		dt, CarSystem.last_time = time() - CarSystem.last_time, time()
		#print( "dt", dt )

		#dt = 1. / 50
		car = ent.get_component( ComponentType.Car )
		phys = ent.get_component( ComponentType.Physics )
		trans = ent.transform()

		wfactor = 1./ (car.cg_to_rear_axle + car.cg_to_front_axle) * \
			car.mass * CarSystem.gravity
		weight_shift = car.cg_height / \
			(car.cg_to_rear_axle + car.cg_to_front_axle) * \
			car.mass * phys.acceleration.length()	#TODO need real accel

		weight_rear = car.cg_to_rear_axle * wfactor - weight_shift
		weight_front = car.cg_to_front_axle * wfactor + weight_shift

		vlat = phys.velocity - trans.up() * trans.up().dot( phys.velocity )
		vlong = phys.velocity - vlat

		rpm = car.wheel_angular_velocity * 60 / 2 / pi

		speed = vlong.length()
		if speed == 0. and car.wheel_angular_velocity == 0.:
			slip_ratio = 0.
		elif speed == 0.:
			slip_ratio = copysign( 1., car.wheel_angular_velocity )
		else:
			slip_ratio = car.wheel_angular_velocity * car.wheel_radius
			sspeed = copysign( speed, vlong.dot( trans.up() ) )
			slip_ratio = ( slip_ratio - sspeed ) / speed

		traction = car.normalized_slip_ratio_force( slip_ratio )
		traction *= weight_rear

		traction_force = trans.up() * traction
		drag = -phys.velocity * car.drag_coefficient * speed
		resistance = -phys.velocity * car.wheel_rolling_resistance
		force = traction_force + drag + resistance

		drive_torque = car.acceleration * car.gears[ car.gear ] * \
			car.differential_ratio * car.torque( rpm )
		traction_torque = -traction * car.wheel_radius
		braking_torque = -car.braking * car.brake_torque
		torque = drive_torque + traction_torque + braking_torque
		#print( "car", speed, slip_ratio, car.wheel_angular_velocity, 
				#force[0], force[1], force[2], torque, drive_torque )

		longsign = 0 if speed == 0. else copysign( 1., vlong.dot(trans.up()) )
		svlat = copysign(vlat.length(), -vlat.dot(trans.right()))
		alpha_front = atan( (svlat + 
			phys.angular_velocity * car.cg_to_front_axle) / 
			max( 1e-5, speed ) ) - \
			car.steering_angle * longsign
		alpha_rear = atan( (svlat -
			phys.angular_velocity * car.cg_to_rear_axle) / 
			max( 1e-5, speed ) )

		latrear_force = weight_rear * \
			car.normalized_slip_angle_force( alpha_rear )
		latfront_force = weight_front * \
			car.normalized_slip_angle_force( alpha_front )

		corner_force = latrear_force + cos( car.steering_angle )*latfront_force
		corner_force = trans.right() * corner_force
		force += corner_force

		car_torque = latrear_force * car.cg_to_rear_axle - \
			cos( car.steering_angle ) * latfront_force * car.cg_to_front_axle
		#print( car.steering_angle, latrear_force, latfront_force, car_torque )

		phys.acceleration += force / phys.mass * 16 # for tile size
		phys.angular_acceleration += car_torque / phys.rotational_inertia *16*16
		car.wheel_angular_velocity += torque / car.wheel_rotational_inertia * dt
		car.wheel_angular_velocity = max( 0., car.wheel_angular_velocity )

