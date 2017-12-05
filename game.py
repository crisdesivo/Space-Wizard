import kivy
kivy.require('1.9.1')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
Window.size = (1000, 600)
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from constants import *
from bullets import * 

#song=SoundLoader.load('sounds/JuhaniJunkala1.wav')
#song.loop=True
#song.play()

Builder.load_string('''
<RotatedImage>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: root.angle
            axis: 0, 0, 1
            origin: root.center
    canvas.after:
        PopMatrix
''')


attacks=[ice_star, lightning, black_hole, fire_bullet, venom_ball, fire_storm, fire_breath, whirlpool, flamenco]

class Arena(Widget):
	def __init__(self, **kwargs):
		super(Arena, self).__init__()

class Platform(Sprite):
	def __init__(self, **kwargs):
		super(Platform, self).__init__(source='images/run_1.png',**kwargs)


class Mage(Sprite):
	def __init__(self, **kwargs):
		super(Mage, self).__init__(source='images/run_1.png',**kwargs)
		self.shooting_down=False
		self.d=False
		self.s=False
		self.w=False
		self.fly=False
		self.shooting=False
		self.x=start_x_position
		self.y=start_y_position
		self.allow_stretch=True
		self.size=(mage_size_x, mage_size_y)
		self.enemies=[]
		self.gravity=gravity
		self.y_velocity=0
		self.x_velocity=0
		self.running_right=False
		self.running_left=False
		self.current_cooldown=0
		self.alive=True
		self.learned_attacks=attacks
		self.chosen_attacks=[flamenco, fire_storm]
		self.Selected_shot=0

	def shoot(self):
		if self.current_cooldown<=0:
			shot=attack_instance(attack=self.chosen_attacks[0], pos=(self.x+shots_x_offset,self.y+shots_y_offset), directionX=self.d-self.shooting_down, directionY=self.w-self.s)
			self.add_widget(shot)
			self.current_cooldown=shot.cooldown

	def take_hit(self, bullet):
		self.alive=False

	def update(self):
		self.current_cooldown-=1
		if self.fly:
 			self.y_velocity=mage_flap_velocity
		self.y_velocity+=self.gravity
		self.y_velocity=max(self.y_velocity,-velocity_cap)
		self.y+=self.y_velocity
		if self.y<0:
			self.y=0
			self.y_velocity=0
		elif self.y>Window.height-self.size[1]:
			self.y=Window.height-self.size[1]
			self.y_velocity=0
		if self.running_right:
			self.x_velocity+=mage_run_acceleration
		elif self.running_left:
			self.x_velocity-=mage_run_acceleration
		if self.x_velocity!=0:
			self.x+=self.x_velocity
			self.x_velocity*=1-friction
			if abs(self.x_velocity)<0.5:
				self.x_velocity=0
		self.x=max(0,min(self.x,Window.width-self.size[0]))

		for child in list(self.children):
			child.update()

class Enemy(Sprite):
	def __init__(self, **kwargs):
		super(Enemy, self).__init__(**kwargs)
		self.start_x=self.x
		self.start_y=self.y
		self.invencible=False
		self.invencibility_cooldown=0
		self.hp_label=Label(text='')
		self.poison=0

	def move(self, mage):
		pass

	def update(self, mage):
		self.hp_label.text=str(self.hp)
		self.hp_label.pos=(self.x+self.width/2,self.y)
		self.invencibility_cooldown-=1
		if self.invencibility_cooldown<=0:
			self.invencible=False
			self.opacity=1
		if randint(0,60)==1:
			self.hp-=self.poison
		self.move(mage)

	def take_hit(self, bullet):
		self.hp -= bullet.damage
		self.invencible=True
		self.opacity=flicker_opacity
		self.invencibility_cooldown=enemy_invincibility_frames
		self.poison+=bullet.poison

	def shoot(self):
		pass

class Head(Enemy):
	def __init__(self, **kwargs):
		super(Head, self).__init__(source='atlas://images/Redshrike/enemy',pos=(head_start_x_position,head_start_y_position))
		self.hp=head_hp
		self.theta=0.0
		self.attack=fire_storm

	def move(self, mage):
		self.theta+=1.0
		self.x=self.start_x+head_radius*cos(self.theta/head_frecuency)
		self.y=self.start_y+head_radius*sin(self.theta/head_frecuency)

	def shoot(self, mage):
		directionX=2* (mage.x>self.x) -1 
		star=attack_instance(pos=(self.x,self.y), attack=self.attack, directionX=directionX, directionY=0)
		self.add_widget(star)

	def update(self, mage):
		super(Head, self).update(mage)
		if randint(0,head_attack_frequency)==1:
			self.shoot(mage)
		for child in list(self.children):
			child_update = getattr(child, "update", None)
			if callable(child_update):
				child_update()

class Head2(Head):
	def __init__(self, **kwargs):
		super(Head2, self).__init__()
		self.attack=sync_shot
	def move(self, mage):
		if mage.y < self.y:
			self.y-=head2_speed
		else:
			self.y+=head2_speed




class Background(Widget):
	def __init__(self, source):
		super(Background, self).__init__()
		self.image = Sprite(source=source)
		self.add_widget(self.image)
		self.size=self.image.size
		self.image_dupe=Sprite(source=source, x=self.width)
		self.add_widget(self.image_dupe)

	def update(self):
		self.image.x -=background_speed
		self.image_dupe.x -=background_speed
		if self.image.right <=0:
			self.image.x=0
			self.image_dupe.x=self.width

class Fight(Widget):
	def __init__(self, enemy, mage, **kwargs):
		super(Fight, self).__init__(**kwargs)
		self.background = Background(source='images/back.png')
		self.map_enemy=enemy
		self.size=self.background.size
		self.add_widget(self.background)
		self.touching=False
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
		self._keyboard.bind(on_key_down=self._on_keyboard_down)
		self._keyboard.bind(on_key_up=self._on_keyboard_up)
		self.enemy=enemy.enemy()
		#self.enemy.size=(self.enemy.size[0]*1.5,self.enemy.size[1]*1.5)
		self.add_widget(self.enemy)
		self.add_widget(self.enemy.hp_label)
		self.mage=mage
		self.add_widget(self.mage)
		self.mage.enemies.append(self.enemy)
		Clock.schedule_interval(self.update, 1.0/framerate)

	def on_touch_down(self, touch):
		if touch.button=='right':
			self.mage.Selected_shot+=1
			if self.mage.Selected_shot==len(attacks):
				self.mage.Selected_shot=0

		else:
			self.touching=True

	def on_touch_up(self, touch):
		if touch.button=='left':
			self.touching=False

	def return_to_world_map(self):
		parent=self.parent
		parent.remove_widget(self)
		w_map=WorldMap()
		for enemy in parent.alive_enemies:
			w_map.map.add_widget(enemy)
		parent.add_widget(w_map)

	#game update
	def update(self, dt):
		if not self.mage.alive or self.enemy.hp<=0:
			return
		else :
			self.background.update()
			if self.mage.shooting:
				self.mage.shoot()
			self.mage.update()
			if self.enemy.hp>0:
				for child in list(self.enemy.children):
					if child.hit(self.mage):
						self.mage.take_hit(child)
				self.enemy.update(self.mage)
				for child in list(self.mage.children):
					if not self.enemy.invencible and self.enemy not in child.avoid and child.hit(self.enemy):
						child.make_hit(self.enemy)

			if not self.mage.alive or self.enemy.hp<=0:
				self.parent.alive_enemies.remove(self.map_enemy)
				if len(self.parent.alive_enemies)==0:
					print ("ganaste")
				self.return_to_world_map()

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard.unbind(on_key_up=self._on_keyboard_up)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		if keycode[1]=='up':
			self.mage.fly=True
		elif keycode[1]=='right':
			self.mage.running_right=True
			self.mage.running_left=False
		elif keycode[1]=='left':
			self.mage.running_left=True
			self.mage.running_right=False
		elif keycode[1]=='d':
			self.mage.d=True
			self.mage.shooting_down=False
			self.mage.shooting=True
		elif keycode[1]=='w':
			self.mage.w=True
			self.mage.s=False
			self.mage.shooting=True
		elif keycode[1]=='a':
			self.mage.shooting_down=True
			self.mage.d=False
			self.mage.shooting=True
		elif keycode[1]=='s':
			self.mage.s=True
			self.mage.w=False
			self.mage.shooting=True
		elif keycode[1]=='q':
			self.mage.chosen_attacks=list(reversed(self.mage.chosen_attacks))
		return True

	def _on_keyboard_up(self, keyboard, keycode):
		if keycode[1]=='right':
			self.mage.running_right=False
		elif keycode[1]=='left':
			self.mage.running_left=False
		elif keycode[1]=='up':
			self.mage.fly=False
		elif keycode[1]=='d':
			self.mage.d=False
		elif keycode[1]=='a':
			self.mage.shooting_down=False
		elif keycode[1]=='s':
			self.mage.s=False
		elif keycode[1]=='w':
			self.mage.w=False
		if not (self.mage.shooting_down or self.mage.s or self.mage.d or self.mage.w):
			self.mage.shooting=False
		return True


class Menu(Widget):
	def __init__(self, **kwargs):
		super(Menu, self).__init__(**kwargs)
		self.add_widget(Label(text='Try again?',pos=(Window.height/2.0,Window.width/2.0)))
	def on_touch_down(self, *ignore):
		parent = self.parent
		parent.remove_widget(self)
		parent.add_widget(Fight(Head2, Mage(), size=Window.size))

class Map2D(Image):
	def __init__(self, source, pos, dx, dy, **kwargs):
		super(Map2D, self).__init__(source=source, pos=pos, **kwargs)
		self.tile_width=dx
		self.tile_height=dy
		self.size = self.texture.size

	def remove_all_widgets(self):
		for child in list(self.children):
			self.remove_widget(child)

	def scroll_right(self):
		self.x+=self.tile_width
		self.x=max(-self.width+Window.width/2+tile_width/2,min(Window.width/2-tile_width/2,self.x))
		for child in list(self.children):
			child.x=child.original_pos[0]+self.x
	def scroll_left(self):
		self.x-=self.tile_width
		self.x=max(-self.width+Window.width/2+tile_width/2,min(Window.width/2-tile_width/2,self.x))
		for child in list(self.children):
			child.x=child.original_pos[0]+self.x
	def scroll_up(self):
		self.y+=self.tile_height
		self.y=max(-self.height+Window.height/2+tile_width/2,min(Window.height/2-tile_width/2,self.y))
		for child in list(self.children):
			child.y=child.original_pos[1]+self.y
	def scroll_down(self):
		self.y-=self.tile_height
		self.y=max(-self.height+Window.height/2+tile_width/2,min(Window.height/2-tile_width/2,self.y))
		for child in list(self.children):
			child.y=child.original_pos[1]+self.y

class MapEnemy(Sprite):
	def __init__(self, Enemy, pos, **kwargs):
		super(MapEnemy, self).__init__(**kwargs)
		self.enemy=Enemy
		self.original_pos=pos
	def fight(self):
		parent=self.parent
		parent.remove_all_widgets()
		grandparent = parent.parent
		level = grandparent.parent
		level.remove_widget(grandparent)
		level.add_widget(Fight(self, Mage(), size=Window.size))

class WorldMap(Widget):
	def __init__(self, **kwargs):
		super(WorldMap, self).__init__(**kwargs)
		self.map=Map2D(source='images/back.png', pos=(0,0), dx=tile_width, dy=tile_width)
		self.add_widget(self.map)
		self.mage_avatar=Sprite(source='images/run_1.png', pos=(Window.width/2,Window.height/2))
		self.mage_avatar.size=(tile_width,tile_width)
		self.mage_avatar.x-=self.mage_avatar.size[0]/2
		self.mage_avatar.y-=self.mage_avatar.size[1]/2
		self.add_widget(self.mage_avatar)
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
		self._keyboard.bind(on_key_down=self._on_keyboard_down)
		self._keyboard.bind(on_key_up=self._on_keyboard_up)

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard.unbind(on_key_up=self._on_keyboard_up)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		if keycode[1]=='up':
			self.map.scroll_down()
		elif keycode[1]=='right':
			self.map.scroll_left()
		elif keycode[1]=='left':
			self.map.scroll_right()
		elif keycode[1]=='down':
			self.map.scroll_up()
		elif keycode[1]=='enter':
			for child in list(self.map.children):
				if self.mage_avatar.collide_widget(child):
					child.fight()

		return True

	def _on_keyboard_up(self, keyboard, keycode):
		pass

class Level1(Widget):
	def __init__(self):
		super(Level1, self).__init__()
		self.alive_enemies={
			MapEnemy(Head, source='atlas://images/Redshrike/enemy', pos=(head_x,head_y)),
			MapEnemy(Head2, source='atlas://images/Redshrike/enemy', pos=(head2_x,head2_y))
			}
		self.world_map=WorldMap()
		for enemy in self.alive_enemies:
			self.world_map.map.add_widget(enemy)
		self.add_widget(self.world_map)

class GameApp(App):
	def __init__(self):
		super(GameApp, self).__init__()
	def build(self):
		return Level1()

if __name__ == "__main__":
	GameApp().run()