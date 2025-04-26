from ggate.const import definitions
from .AND import AND
from .GND import GND
from .NAND import NAND
from .NOR import NOR
from .NOT import NOT
from .OR import OR
from .OSC import OSC
from .SW import SW
from .TSB import TSB
from .VDD import VDD
from .XOR import XOR

STANDARD_COMPONENTS = {
  definitions.component_AND     :  AND(),
  definitions.component_GND     :  GND(),
  definitions.component_NAND    : NAND(),
  definitions.component_NOR     :  NOR(),
  definitions.component_NOT     :  NOT(),
  definitions.component_OR      :   OR(),
  definitions.component_OSC     :  OSC(),
  definitions.component_SW      :   SW(),
  definitions.component_tribuff :  TSB(),
  definitions.component_VDD     :  VDD(),
  definitions.component_XOR     :  XOR(),
}