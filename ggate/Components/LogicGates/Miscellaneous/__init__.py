from ggate.const import definitions
from .Probe import Probe
from .Text import Text

MISC_COMPONENTS = {
    definitions.component_probe: Probe(),
    definitions.component_text: Text(),
}