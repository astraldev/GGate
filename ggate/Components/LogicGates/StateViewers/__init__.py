from ggate.const import definitions
from .SevenSegment import SevenSegment
from .LED import LED

STATE_VIEWER_COMPONENTS = {
    definitions.component_LED: LED(),
    definitions.component_7seg: SevenSegment(),
}