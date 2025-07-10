# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from gettext import gettext as _
from ggate.const import definitions

from . import Calculator
from .Counters import COUNTERS
from .FlipFlops import FLIP_FLOPS
from .Standard import STANDARD_COMPONENTS
from .Miscellaneous import MISC_COMPONENTS
from .SystemComponents import BaseComponent
from .StateViewers import STATE_VIEWER_COMPONENTS

logic_gates: dict[definitions, BaseComponent] = {
  definitions.component_none: None,
  definitions.component_net: None,
  definitions.component_adder: Calculator.Adder(),
}

logic_gates.update(COUNTERS)
logic_gates.update(FLIP_FLOPS)
logic_gates.update(STATE_VIEWER_COMPONENTS)
logic_gates.update(MISC_COMPONENTS)
logic_gates.update(STANDARD_COMPONENTS)

[c.set_rot_props() for c in logic_gates.values() if c]
