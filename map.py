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
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from constants import *
from bullets import * 
from kivy.lang import Builder
from game import *

class Map2D(Image):
	def __init__(self, source, pos, dx, dy, **kwargs):
		super(Map2D, self).__init__(source=source, pos=pos, **kwargs)
		self.tile_width=dx
		self.tile_height=dy
		self.size = self.texture.size
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
	def __init__(self, enemy, **kwargs):
		super(MapEnemy, self).__init__(**kwargs)
		self.enemy=enemy
	def fight(self):
		print ("PELEA")

class WorldMap(Widget):
	def __init__(self, **kwargs):
		super(Game, self).__init__(**kwargs)
		self.map=Map2D(source='images/back.png', pos=(0,0), dx=tile_width, dy=tile_width)
		self.add_widget(self.map)
		self.mage_avatar=Sprite(source='images/run_1.png', pos=(Window.width/2,Window.height/2))
		self.mage_avatar.size=(tile_width,tile_width)
		self.mage_avatar.x-=self.mage_avatar.size[0]/2
		self.mage_avatar.y-=self.mage_avatar.size[1]/2
		self.add_widget(self.mage_avatar)
		self.head=MapEnemy(Head, source='atlas://images/Redshrike/enemy', pos=(500,1000))
		self.head.original_pos=(500,1000)
		self.map.add_widget(self.head)
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