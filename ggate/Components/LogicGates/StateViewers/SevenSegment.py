import cairo
from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths
from ggate.const import definitions
from gettext import gettext as _

class SevenSegment(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("Seven-segment display")
    self.comp_rect = [10, -80, 100, 0]
    self.input_pins = [(10, -70), (10, -50), (10, -30), (10, -10)]
    self.output_pins = []
    self.input_pins_dir = [definitions.direction_E, definitions.direction_E, definitions.direction_E, definitions.direction_E]
    self.output_pins_dir = []
    self.input_level = [False, False, False, False]
    self.output_level = []

    self.prop_names = ['_red', '_blue', '_green', '_yellow']
    self.properties.append((_("Color of 7 Segment LEDs :"), None, ''))
    self.properties.append((_("Color :"), (definitions.property_select, _('Red'), _('Blue'), _('Green'), _('Yellow')), ''))
    self.values.append(2)

  def set_7seg(self, cr: cairo.Context, a, b, c, d, e, f, g):

    color = self.prop_names[self.values[0]]
    high_color = Preference[color] if self.prop_names[self.values[0]] is not None else Preference['_green']

    if a:
      cr.set_source(high_color)
      cairo_paths(cr, (60, -70), (62, -68), (88, -68), (90, -70), (88, -72), (62, -72), (60, -70))
      cr.fill()

    if b:
      cr.set_source(high_color)
      cairo_paths(cr, (90, -70), (88, -68), (88, -42), (90, -40), (92, -42), (92, -68), (90, -70))
      cr.fill()

    if c:
      cr.set_source(high_color)
      cairo_paths(cr, (90, -40), (88, -38), (88, -12), (90, -10), (92, -12), (92, -38), (90, -40))
      cr.fill()

    if d:
      cr.set_source(high_color)
      cairo_paths(cr, (60, -10), (62, -8), (88, -8), (90, -10), (88, -12), (62, -12), (60, -10))
      cr.fill()

    if e:
      cr.set_source(high_color)
      cairo_paths(cr, (60, -40), (58, -38), (58, -12), (60, -10), (62, -12), (62, -38), (60, -40))
      cr.fill()

    if f:
      cr.set_source(high_color)
      cairo_paths(cr, (60, -70), (58, -68), (58, -42), (60, -40), (62, -42), (62, -68), (60, -70))
      cr.fill()

    if g:
      cr.set_source(high_color)
      cairo_paths(cr, (60, -40), (62, -38), (88, -38), (90, -40), (88, -42), (62, -42), (60, -40))
      cr.fill()




  def drawComponent(self, cr, layout):
    cairo_paths(cr, (60, -70), (62, -68), (88, -68), (90, -70), (88, -72), (62, -72), (60, -70))
    cairo_paths(cr, (90, -70), (88, -68), (88, -42), (90, -40), (92, -42), (92, -68), (90, -70))
    cairo_paths(cr, (90, -40), (88, -38), (88, -12), (90, -10), (92, -12), (92, -38), (90, -40))
    cairo_paths(cr, (60, -10), (62, -8), (88, -8), (90, -10), (88, -12), (62, -12), (60, -10))
    cairo_paths(cr, (60, -40), (58, -38), (58, -12), (60, -10), (62, -12), (62, -38), (60, -40))
    cairo_paths(cr, (60, -70), (58, -68), (58, -42), (60, -40), (62, -42), (62, -68), (60, -70))
    cairo_paths(cr, (60, -40), (62, -38), (88, -38), (90, -40), (88, -42), (62, -42), (60, -40))
    cr.rectangle(30, -80, 70, 80)
    cr.stroke()
    cairo_draw_text(cr, layout, "IA", 35, -70, 0.0, 0.5)
    cairo_draw_text(cr, layout, "IB", 35, -50, 0.0, 0.5)
    cairo_draw_text(cr, layout, "IC", 35, -30, 0.0, 0.5)
    cairo_draw_text(cr, layout, "ID", 35, -10, 0.0, 0.5)
    cr.fill()


  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (10, -70), (30, -70))
    cairo_paths(cr, (10, -50), (30, -50))
    cairo_paths(cr, (10, -30), (30, -30))
    cairo_paths(cr, (10, -10), (30, -10))
    cr.stroke()


  def drawComponentRunOverlap(self, cr, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -70), (30, -70))
    cr.stroke()
    if self.input_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -50), (30, -50))
    cr.stroke()
    if self.input_level[2]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -30), (30, -30))
    cr.stroke()
    if self.input_level[3]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -10), (30, -10))
    cr.stroke()
    # Draw 7seg
    if not self.input_level[0] and not self.input_level[1] and not self.input_level[2] and not self.input_level[3]:
      # 0
      self.set_7seg(cr, True, True, True, True, True, True, False)
    elif not self.input_level[0] and not self.input_level[1] and not self.input_level[2] and self.input_level[3]:
      # 1
      self.set_7seg(cr, False, True, True, False, False, False, False)
    elif not self.input_level[0] and not self.input_level[1] and self.input_level[2] and not self.input_level[3]:
      # 2
      self.set_7seg(cr, True, True, False, True, True, False, True)
    elif not self.input_level[0] and not self.input_level[1] and self.input_level[2] and self.input_level[3]:
      # 3
      self.set_7seg(cr, True, True, True, True, False, False, True)
    elif not self.input_level[0] and self.input_level[1] and not self.input_level[2] and not self.input_level[3]:
      # 4
      self.set_7seg(cr, False, True, True, False, False, True, True)
    elif not self.input_level[0] and self.input_level[1] and not self.input_level[2] and self.input_level[3]:
      # 5
      self.set_7seg(cr, True, False, True, True, False, True, True)
    elif not self.input_level[0] and self.input_level[1] and self.input_level[2] and not self.input_level[3]:
      # 6
      self.set_7seg(cr, True, False, True, True, True, True, True)
    elif not self.input_level[0] and self.input_level[1] and self.input_level[2] and self.input_level[3]:
      # 7
      self.set_7seg(cr, True, True, True, False, False, False, False)
    elif self.input_level[0] and not self.input_level[1] and not self.input_level[2] and not self.input_level[3]:
      # 8
      self.set_7seg(cr, True, True, True, True, True, True, True)
    elif self.input_level[0] and not self.input_level[1] and not self.input_level[2] and self.input_level[3]:
      # 9
      self.set_7seg(cr, True, True, True, True, False, True, True)
    elif self.input_level[0] and not self.input_level[1] and self.input_level[2] and not self.input_level[3]:
      # A
      self.set_7seg(cr, True, True, True, False, True, True, True)
    elif self.input_level[0] and not self.input_level[1] and self.input_level[2] and self.input_level[3]:
      # B
      self.set_7seg(cr, False, False, True, True, True, True, True)
    elif self.input_level[0] and self.input_level[1] and not self.input_level[2] and not self.input_level[3]:
      # C
      self.set_7seg(cr, True, False, False, True, True, True, False)
    elif self.input_level[0] and self.input_level[1] and not self.input_level[2] and self.input_level[3]:
      # D
      self.set_7seg(cr, False, True, True, True, True, False, True)
    elif self.input_level[0] and self.input_level[1] and self.input_level[2] and not self.input_level[3]:
      # E
      self.set_7seg(cr, True, False, False, True, True, True, True)
    else:
      # F
      self.set_7seg(cr, True, False, False, False, True, True, True)

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 97 and self.pos_y - 77 <= y <= self.pos_y - 3:
      return True
    return False