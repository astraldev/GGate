from ggate.const import definitions
from .ModNCounter import ModNCounter
from .PISOShiftRegister import PISOShiftRegister
from .PIPOShiftRegister import PIPOShiftRegister
from .SIPOShiftRegister import SIPOShiftRegister
from .SISOShiftRegister import SISOShiftRegister

COUNTERS = {
  definitions.component_counter : ModNCounter(),
  definitions.component_SISO    : SISOShiftRegister(),
  definitions.component_SIPO    : SIPOShiftRegister(),
  definitions.component_PISO    : PISOShiftRegister(),
  definitions.component_PIPO    : PIPOShiftRegister(),
}