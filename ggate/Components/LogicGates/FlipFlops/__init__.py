from ggate.const import definitions
from .DFF import DFF
from .TFF import TFF
from .JKFF import JKFF
from .RSFF import RSFF

FLIP_FLOPS = {
  definitions.component_RSFF :  RSFF(),
  definitions.component_JKFF :  JKFF(),
  definitions.component_DFF  :  DFF(),
  definitions.component_TFF  :  TFF(),
}