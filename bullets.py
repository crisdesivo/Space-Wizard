from constants import *
from kivy.clock import Clock
from kivy.uix.image import Image
from random import randint
from math import *
from kivy.properties import NumericProperty

def attack_instance(attack, pos, directionX, directionY):
	return attack["pattern"](pos=pos, attack=attack, directionX=directionX, directionY=directionY)

def remove_widget(widget):
	parent=widget.parent
	parent.remove_widget(widget)


class RotatedImage(Image):
	angle = NumericProperty()

class Sprite(RotatedImage):
	def __init__(self, **kwargs):
		super(Sprite, self).__init__(**kwargs)
		self.allow_stretch=True
		self.texture.mag_filter='nearest'
		self.size = self.texture.size

class Bullet(Sprite):
	def __init__(self, **kwargs):
		super(Bullet, self).__init__(**kwargs)
		self.avoid=[]
		self.poison=0
	def hit(self,enemy):
		return enemy.collide_point(self.center_x,self.center_y)
	def make_hit(self,enemy):
		enemy.take_hit(self)
		remove_widget(self)
	def out_of_range(self):
		return self.x>Window.width or self.x<0 or self.y<-Window.height or self.y>2*Window.height

class Star(Bullet):
	def __init__(self, pos, attack, directionX, directionY):
		super(Star, self).__init__(source=attack["image_source"],pos=pos)
		self.x_velocity=randint(attack["min_x_speed"], attack["max_x_speed"])
		self.y_velocity=randint(-attack["max_y_speed"], attack["max_y_speed"])
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.axis1=0
		self.axis2=0
		self.directionX=directionX/sqrt(directionX**2+directionY**2)
		self.directionY=directionY/sqrt(directionX**2+directionY**2)
	def update(self):
		self.axis1=self.x_velocity
		self.axis2=self.y_velocity
		self.x+=self.axis1*self.directionX + self.axis2*self.directionY
		self.y+=self.axis1*self.directionY - self.axis2*self.directionX
		if self.out_of_range():
			self.parent.remove_widget(self)

ice_star={
	"damage":1,
	"cooldown": 5,
	"min_x_speed": 10,
	"max_x_speed": 20,
	"max_y_speed": 1,
	"image_source": 'atlas://images/Master484/cyan_star',
	"type": "ice",
	"pattern": Star
}

class Bomb(Bullet):
	def __init__(self, pos, attack, directionX, directionY):
		super(Bomb, self).__init__(source=attack["image_source"],pos=pos)
		self.attack=attack
		self.velocity=attack["velocity"]
		self.y_velocity=0
		self.starting_y_speed=attack["y_speed"]
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.axis1=0
		self.axis2=0
		self.directionX=directionX/sqrt(directionX**2+directionY**2)
		self.directionY=directionY/sqrt(directionX**2+directionY**2)
	def update(self):
		self.axis1=self.velocity
		self.axis2=self.y_velocity
		self.x+=self.axis1*self.directionX + self.axis2*self.directionY
		self.y+=self.axis1*self.directionY - self.axis2*self.directionX
		if self.out_of_range():
			self.parent.remove_widget(self)
	def make_hit(self, enemy):
		enemy.take_hit(self)
		if self.damage>=1:
			parent=self.parent
			bomb1=attack_instance(pos=self.pos, attack=self.attack)
			bomb1.damage=self.damage/2.0
			bomb1.y_velocity=self.starting_y_speed
			bomb1.avoid=self.avoid
			bomb1.avoid.append(enemy)
			bomb2=attack_instance(pos=self.pos, attack=self.attack)
			bomb2.damage=self.damage/2.0
			bomb2.y_velocity=-self.starting_y_speed
			bomb2.avoid=self.avoid
			bomb2.avoid.append(enemy)
			parent.add_widget(bomb1)
			parent.add_widget(bomb2)
			parent.remove_widget(self)
		else:
			remove_widget(self)

fire_bomb={
	"damage":10,
	"velocity":5,
	"cooldown":30,
	"y_speed": 2,
	"image_source": "atlas://images/Master484/red_bomb",
	"pattern": Bomb
}


class Random(Bullet):
	def __init__(self, pos, attack, directionX, directionY):
		super(Random,self).__init__(source=attack["image_source"],pos=pos)
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.velocity=attack["velocity"]
		self.axis1=0
		self.axis2=0
		self.directionX=directionX/sqrt(directionX**2+directionY**2)
		self.directionY=directionY/sqrt(directionX**2+directionY**2)
	def update(self):
		self.axis1=randint(0,self.velocity)
		self.axis2=randint(-self.velocity,self.velocity)
		self.x+=self.axis1*self.directionX + self.axis2*self.directionY
		self.y+=self.axis1*self.directionY - self.axis2*self.directionX
		if self.out_of_range():
			remove_widget(self)

black_hole={
	"damage":10,
	"cooldown": 30,
	"velocity": 10,
	"image_source": "atlas://images/Master484/my_pellet",
	"pattern": Random
}

class Quick(Bullet):
	def __init__(self, pos, attack, directionX, directionY):
		super(Quick,self).__init__(source=attack["image_source"],pos=pos)
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.velocity=attack["velocity"]
		self.directionX=directionX/sqrt(directionX**2+directionY**2)
		self.directionY=directionY/sqrt(directionX**2+directionY**2)
		self.axis1=0
		self.axis2=0
		self.angle=atan2(directionY,directionX)*180/pi
	def update(self):
		self.axis1=self.velocity
		self.x+=self.axis1*self.directionX + self.axis2*self.directionY
		self.y+=self.axis1*self.directionY - self.axis2*self.directionX
		if self.out_of_range():
			remove_widget(self)

fire_bullet={
	"pattern": Quick,
	"image_source": "atlas://images/Master484/quick_bullet",
	"damage": 1,
	"cooldown": 5,
	"velocity": 20
}

class Gravity(Bullet):
	def __init__(self, pos, attack, directionX, directionY):
		super(Gravity,self).__init__(source=attack["image_source"],pos=pos)
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.velocity=attack["velocity"]
		self.poison=attack["poison"]
		self.axis1=0
		self.axis2=0
		self.directionX=directionX/sqrt(directionX**2+directionY**2)
		self.directionY=directionY/sqrt(directionX**2+directionY**2)
		self.velocity_y=directionY*attack["velocity_y"]
		self.gravity=gravity
	def update(self):
		self.x+=self.velocity*self.directionX
		self.velocity_y+=self.gravity
		self.y+=self.velocity_y
		if self.out_of_range():
			remove_widget(self)

venom_ball={
	"damage": 5,
	"velocity": 10,
	"velocity_y": 10,
	"cooldown": 60,
	"image_source": 'atlas://images/Master484/snake',
	"pattern": Gravity,
	"poison":1
}



class Periodic(Bullet):
	def __init__(self, pos, attack, directionX, directionY):
		super(Periodic,self).__init__(source=attack["image_source"],pos=pos)
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.velocity=attack["velocity"]
		self.amplitude=attack["amplitude"]
		self.frequency=attack["frequency"]
		self.axis1=0
		self.axis2=0
		self.directionX=directionX/sqrt(directionX**2+directionY**2)
		self.directionY=directionY/sqrt(directionX**2+directionY**2)
		self.initial_position=pos
		self.offset=randint(0,180)
		self.t=0.0
	def update(self):
		self.axis1=self.t*self.velocity
		self.axis2=self.amplitude*(sin( (self.t+self.offset)/self.frequency)-sin(self.offset/self.frequency))
		self.x=self.initial_position[0]+self.axis1*self.directionX + self.axis2*self.directionY
		self.y=self.initial_position[1]+self.axis1*self.directionY - self.axis2*self.directionX
		self.t+=1.0
		if self.out_of_range():
			remove_widget(self)

leaf_storm={
	"pattern": Periodic,
	"image_source": "atlas://images/Master484/green_shuriken",
	"damage": 2,
	"cooldown": 10,
	"velocity": Window.width*0.005,
	"amplitude": Window.height*0.1,
	"frequency": 5
}

whirlpool={
	"pattern": Periodic,
	"image_source": "atlas://images/Master484/bubble",
	"damage": 12,
	"cooldown": 30,
	"velocity": Window.width*0.004,
	"amplitude": Window.height*0.2,
	"frequency": 30
}

fire_storm={
	"pattern": Periodic,
	"image_source": "atlas://images/Master484/red_bomb",
	"damage": 1,
	"cooldown": 10,
	"velocity": Window.width*0.007,
	"amplitude": Window.height*0.1,
	"frequency": 5
}

class Fire(Bullet):
	def __init__(self,pos,attack, directionX, directionY):
		super(Fire, self).__init__(source=attack["image_source"],pos=pos)
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.initial_position=pos
		self.angle=randint(-attack["angle"],attack["angle"])
		self.velocity=attack["velocity"]
		self.min_opacity=attack["opacity"]
		self.duration=attack["duration"]
		self.constant=attack["constant"]
		self.t=0
		self.axis1=0
		self.axis2=0
		self.directionX=directionX/sqrt(directionX**2+directionY**2)
		self.directionY=directionY/sqrt(directionX**2+directionY**2)
	def update(self):
		self.t+=1
		self.axis1=self.velocity*cos(2*pi*self.angle/360)
		self.axis2=self.velocity*sin(2*pi*self.angle/360)*self.constant**self.t
		self.x+=self.axis1*self.directionX + self.axis2*self.directionY
		self.y+=self.axis1*self.directionY - self.axis2*self.directionX
		self.opacity-=(1-self.min_opacity)/self.duration
		if self.t>self.duration or self.out_of_range():
			remove_widget(self)

fire_breath={
	"pattern": Fire,
	"image_source": "atlas://images/Master484/red_bomb",
	"damage": 1,
	"cooldown": 4,
	"angle": 30,
	"velocity": 10,
	"duration": 16,
	"constant":0.99,
	"opacity": 0.1
}

bubbles={
	"pattern": Fire,
	"image_source": "atlas://images/Master484/bubble",
	"damage": 10,
	"cooldown": 12,
	"angle": 60,
	"velocity": 6,
	"duration": 50,
	"constant":0.9,
	"opacity": 0.5
}

lightning={
	"pattern": Fire,
	"image_source": "atlas://images/Master484/yellow_rod1",
	"damage": 1,
	"cooldown": 2,
	"angle": 45,
	"velocity": 25,
	"duration": 7,
	"constant":1,
	"opacity": 1
}

class Mirror(Bullet):
	def __init__(self, pos, attack, directionX, directionY):
		super(Mirror, self).__init__(source=attack["image_source"],pos=pos)
		self.size=(attack["width"],attack["height"])
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.directionX=directionX/sqrt(directionX**2+directionY**2)
		self.directionY=directionY/sqrt(directionX**2+directionY**2)
		self.axis1=0
		self.axis2=0
		self.x_velocity=attack["velocity"]
	def hit(self,enemy):
		return enemy.collide_point(self.center_x, self.center_y)
	def update(self):
		self.axis1=self.x_velocity
		self.y=self.parent.y+shots_y_offset
		self.x+=self.axis1*self.directionX
		if self.out_of_range():
			remove_widget(self)

sync_shot={
	"pattern": Mirror,
	"image_source": "atlas://images/Master484/mirror_bullet",
	"width": 50,
	"height": 40,
	"damage": 5,
	"cooldown": 150,
	"velocity": 5
}

class Homing(Bullet):
	def __init__(self,pos,attack, directionX, directionY):
		super(Homing, self).__init__(source=attack["image_source"],pos=pos)
		self.damage=attack["damage"]
		self.cooldown=attack["cooldown"]
		self.velocity=attack["velocity"]
	def update(self):
		enemy=self.parent.enemies[0]
		dx=enemy.center_x-self.x
		dy=enemy.center_y-self.y
		distance=sqrt(dx**2+dy**2)
		self.x+=self.velocity*dx/distance
		self.y+=self.velocity*dy/distance

flamenco={
	"image_source": "atlas://images/Master484/pink_shuriken",
	"pattern": Homing,
	"damage": 2,
	"cooldown": 50,
	"velocity": 20
}