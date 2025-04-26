# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from gi.repository import Pango, PangoCairo
from ggate.const import definitions as const
import cairo

def number_in_range(value, min_value, max_value):
  return min_value <= value <= max_value

def clamp(value, min_value=0, max_value=1):
  return max(min_value, min(value, max_value))

def cairo_paths(cr, *points):
  cr.move_to(points[0][0], points[0][1])
  for p in points[1:]:
    cr.line_to(p[0], p[1])

def cairo_bezier(cr, *points):
  cr.move_to(points[0], points[1])
  cr.curve_to(points[2], points[3], points[4], points[5], points[6], points[7])

def cairo_draw_text(cr, layout, text, x, y, xalign=0.0, yalign=0.0):
  m = cr.get_matrix()
  cr.translate(x, y)
  if m[0] < 0:
    cr.scale(-1, 1)
    xalign = 1.0 - xalign
  if m[3] < 0:
    cr.scale(1, -1)
    yalign = 1.0 - yalign
  if m[1] * m[2] > 0:
    cr.scale(-1, 1)
    xalign = 1.0 - xalign
  layout.set_text(text, -1)
  (w, h) = layout.get_size()
  cr.translate(-w / Pango.SCALE * xalign, -h / Pango.SCALE * yalign)
  PangoCairo.update_layout(cr, layout)
  PangoCairo.show_layout(cr, layout)
  cr.set_matrix(m)

def encode_text(text):
  t_text = ""
  for c in text:
    if c == "\\":
      t_text += "\\\\"
    elif c == ",":
      t_text += "\\c"
    elif c == "=":
      t_text += "\\e"
    elif c == ":":
      t_text += "\\s"
    else:
      t_text += c
  return t_text

def decode_text(text):
  t_text = ""
  esc = False
  for c in text:
    if esc:
      if c == "\\":
        t_text += "\\"
      elif c == "c":
        t_text += ","
      elif c == "e":
        t_text += "="
      elif c == "s":
        t_text += ":"
      esc = False
    elif c == "\\":
      esc = True
    else:
      t_text += c
  return t_text

def stack_with_tphl_lh(time, current, stacks, newdatas, tp_hl, tp_lh):
  for i, dat in enumerate(current):
    if stacks[i] and newdatas[i] == stacks[i][-1][1]:
      continue
    if newdatas[i] == dat:
      stacks[i] = []
    else:
      if dat:
        stacks[i] = [[time + tp_hl, newdatas[i]]]
      else:
        stacks[i] = [[time + tp_lh, newdatas[i]]]

def get_components_rect(components):
  if components:
    x_positions = []
    y_positions = []
    for c in components:
      if c[0] == const.component_net:
        x_positions.append(c[1])
        x_positions.append(c[3])
        y_positions.append(c[2])
        y_positions.append(c[4])
      else:
        x_positions.append(c[1].pos_x + c[1].rot_comp_rect[0])
        x_positions.append(c[1].pos_x + c[1].rot_comp_rect[2])
        y_positions.append(c[1].pos_y + c[1].rot_comp_rect[1])
        y_positions.append(c[1].pos_y + c[1].rot_comp_rect[3])

    return [min(x_positions), min(y_positions), max(x_positions), max(y_positions)]

def rotate_left_90(x, y, orig_x, orig_y):
  return (y - orig_y + orig_x, -x + orig_x + orig_y)

def rotate_right_90(x, y, orig_x, orig_y):
  return (-y + orig_y + orig_x, x - orig_x + orig_y)

def multiply_matrix(X, Y):
  return (X[0] * Y[0] + X[1] * Y[2], X[0] * Y[1] + X[1] * Y[3],
          X[2] * Y[0] + X[3] * Y[2], X[2] * Y[1] + X[3] * Y[3])

def inv_matrix(m):
  det = m[0] * m[3] - m[1] * m[2]
  return (m[3] / det, -m[1] / det, -m[2] / det, m[0] / det)

def fit_components(components, width, height):
  rect = get_components_rect(components)
  if rect[0] < 0:
    for c in components:
      if c[0] == const.component_net:
        c[1] -= rect[0]
        c[3] -= rect[0]
      else:
        c[1].pos_x -= rect[0]
  elif rect[2] > width:
    for c in components:
      if c[0] == const.component_net:
        c[1] -= rect[2] - width
        c[3] -= rect[2] - width
      else:
        c[1].pos_x -= rect[2] - width
  if rect[1] < 0:
    for c in components:
      if c[0] == const.component_net:
        c[2] -= rect[1]
        c[4] -= rect[1]
      else:
        c[1].pos_y -= rect[1]
  elif rect[3] > height:
    for c in components:
      if c[0] == const.component_net:
        c[2] -= rect[3] - height
        c[4] -= rect[3] - height
      else:
        c[1].pos_y -= rect[3] - height

def create_component_matrix(c):
  return cairo.Matrix(
    xx=c[1].matrix[0],
    xy=c[1].matrix[1],
    yx=c[1].matrix[2],
    yy=c[1].matrix[3]
  )

def draw_rounded_rectangle(cr, x, y, width, height, radius = 5):
  if width < 0:
    x += width
    width = abs(width)

  if height < 0:
    y += height
    height = abs(height)

  # Ensure the radius is not too large
  radius = min(radius, width / 2, height / 2)

  # Start drawing the rounded rectangle
  cr.new_sub_path()
  cr.arc(x + width - radius, y + radius, radius, -90 * (3.14 / 180), 0)
  cr.arc(x + width - radius, y + height - radius, radius, 0, 90 * (3.14 / 180))
  cr.arc(x + radius, y + height - radius, radius, 90 * (3.14 / 180), 180 * (3.14 / 180))
  cr.arc(x + radius, y + radius, radius, 180 * (3.14 / 180), 270 * (3.14 / 180))
  cr.close_path()