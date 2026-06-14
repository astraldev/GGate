# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

def ease_out_cubic(t: float) -> float:
	return 1.0 - (1.0 - t) ** 3

class Vector2DAnimation:
	def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], duration_ms: float):
		self.start_pos = list(start_pos)
		self.target_pos = list(target_pos)
		self.current_pos = list(start_pos)
		self.duration_us = duration_ms * 1000.0
		self.elapsed_us = 0.0
		self.completed = False

	def update(self, delta_us: float) -> None:
		self.elapsed_us += delta_us
		if self.elapsed_us >= self.duration_us:
			self.current_pos = list(self.target_pos)
			self.completed = True
		else:
			t = self.elapsed_us / self.duration_us
			eased_t = ease_out_cubic(t)
			self.current_pos[0] = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * eased_t
			self.current_pos[1] = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * eased_t

class CanvasAnimationController:
	def __init__(self, draw_area):
		self.draw_area = draw_area
		self.active_animations = {}
		self.tick_id = None
		self.last_frame_time = 0

	def start_offset_animation(self, item_ref, start_offset: tuple[float, float], duration_ms: float = 150.0) -> None:
		actual_start = start_offset
		if item_ref in self.active_animations:
			actual_start = self.active_animations[item_ref].current_pos

		if actual_start[0] == 0.0 and actual_start[1] == 0.0:
			if item_ref in self.active_animations:
				del self.active_animations[item_ref]
			return

		self.active_animations[item_ref] = Vector2DAnimation(actual_start, (0.0, 0.0), duration_ms)

		if self.tick_id is None:
			self.last_frame_time = 0
			self.tick_id = self.draw_area.drawingarea.add_tick_callback(self._on_tick)

	def cancel_animation(self, item_ref) -> None:
		if item_ref in self.active_animations:
			del self.active_animations[item_ref]
		if not self.active_animations:
			self._stop_tick()

	def clear(self) -> None:
		self.active_animations.clear()
		self._stop_tick()

	def get_visual_offset(self, item_ref) -> tuple[float, float]:
		if item_ref in self.active_animations:
			pos = self.active_animations[item_ref].current_pos
			return pos[0], pos[1]
		return 0.0, 0.0

	def _on_tick(self, widget, frame_clock, user_data=None) -> bool:
		frame_time = frame_clock.get_frame_time()
		if self.last_frame_time == 0:
			self.last_frame_time = frame_time
			return True

		delta_us = frame_time - self.last_frame_time
		self.last_frame_time = frame_time

		completed_keys = []
		for key, anim in self.active_animations.items():
			anim.update(delta_us)
			if anim.completed:
				completed_keys.append(key)

		for key in completed_keys:
			del self.active_animations[key]

		self.draw_area.queue_draw()

		if not self.active_animations:
			self.tick_id = None
			self.last_frame_time = 0
			return False
		return True

	def _stop_tick(self) -> None:
		if self.tick_id is not None:
			self.draw_area.drawingarea.remove_tick_callback(self.tick_id)
			self.tick_id = None
			self.last_frame_time = 0
