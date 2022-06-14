# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from gettext import gettext as _
from glogic import const
from glogic.Components import SystemComponents, Standard, FlipFlop, StateViewer, Misc, Counter, Calculator

comp_dict = {
	const.component_none:    None,
	const.component_net:     None,
	const.component_probe:   SystemComponents.Probe(),
	const.component_VDD:     Standard.VDD(),
	const.component_GND:     Standard.GND(),
	const.component_SW:      Standard.SW(),
	const.component_NOT:     Standard.NOT(),
	const.component_AND:     Standard.AND(),
	const.component_OR:      Standard.OR(),
	const.component_XOR:     Standard.XOR(),
	const.component_NAND:    Standard.NAND(),
	const.component_NOR:     Standard.NOR(),
	const.component_OSC:     Standard.OSC(),
	const.component_RSFF:    FlipFlop.RSFF(),
	const.component_JKFF:    FlipFlop.JKFF(),
	const.component_DFF:     FlipFlop.DFF(),
	const.component_TFF:     FlipFlop.TFF(),
	const.component_counter: Counter.ModNCounter(),
	const.component_SISO:    Counter.SISOShiftRegister(),
	const.component_SIPO:    Counter.SIPOShiftRegister(),
	const.component_PISO:    Counter.PISOShiftRegister(),
	const.component_PIPO:    Counter.PIPOShiftRegister(),
	const.component_adder:   Calculator.Adder(),
	const.component_7seg:    StateViewer.SevenSegment(),
	const.component_LED:     StateViewer.LED(),
	const.component_text:    Misc.Text()
}

for c in comp_dict.values():
	if c:
		c.set_rot_props()
