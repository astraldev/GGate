# ChangeLog

## Version 4.0.0-rc
 Optimized to work on WSL
 Rename project to aid publishing.
 Fix TimingDiagram UI


## Version 3.1.0

 Added a frame to all settings
 Added .glc mime type and icon

## Version 3.0.0

 Added different colors to LED component and 7 Segment display
 Updated UI
 Removed top ToolBar and MenuBar
 Added side pane for components
 Added menu popup for drawing area
 update UI
 switched build tool from Make to setup
 ported to Gtk 4.0
 added menu to drawing area
 removed top menu bar and toolbar

## 2012-11-01  Koichi Akabe  <vbkaisetsu@gmail.com>

 release version 2.6
 update help and translation template

## 2012-10-31  Koichi Akabe  <vbkaisetsu@gmail.com>

 add bzr revno to the about dialog
 update translation template
 apply matrix to picked components
 rename: "swap" to "flip"

## 2012-10-30  Koichi Akabe  <vbkaisetsu@gmail.com>

 add version information to glc format

## 2012-10-28  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix matrix calcuration
 update image exporter to support matrix
 update NEWS and help

## 2012-10-27  Koichi Akabe  <vbkaisetsu@gmail.com>

 update translation template
 support rotation and mirroring
 support middle button drag
 support Python 2.6 or later

## 2012-10-26  Koichi Akabe  <vbkaisetsu@gmail.com>

 add a new script to Makefile.am

## 2012-10-19  Koichi Akabe  <vbkaisetsu@gmail.com>

 update translation template
 update NEWS
 support copy and paste

## 2012-10-17  Koichi Akabe  <vbkaisetsu@gmail.com>

 initialize output of flip-flops
 fix bugs on drawing functions
 split components_to_string and string_to_components from save/open functions

## 2012-10-14  Koichi Akabe  <vbkaisetsu@gmail.com>

 add component names to shift registers
 update Makefile.in

## 2012-10-13  Koichi Akabe  <vbkaisetsu@gmail.com>

 add equivalent circuit of SIPO shift register for documentation
 fix documentation to replace probe button's image
 update NEWS and TODO
 add new image files to a makefile
 update translation templates
 update help files
 support triple input for basic components

## 2012-10-12  Koichi Akabe  <vbkaisetsu@gmail.com>

 add a documentation
 update NEWS
 add help for the pause mode
 add English documentation for C locale

## 2012-10-08  Koichi Akabe  <vbkaisetsu@gmail.com>

 add help contents (Japanese)

## 2012-10-10  Koichi Akabe  <vbkaisetsu@gmail.com>

 add a pause button to keep the state when components are clicked
 add SR and SL ports to PIPO shift register

## 2012-10-06  Koichi Akabe  <vbkaisetsu@gmail.com>

 update translation template
 update NEWS
 add new components: SIPO, PISO, PIPO shift registers

## 2012-10-05  Koichi Akabe  <vbkaisetsu@gmail.com>

 add a new component: Adder

## 2012-10-04  Koichi Akabe  <vbkaisetsu@gmail.com>

 add a new component: SISO shift register
 rename "Counter" to "Mod-N counter"
 add "Number of bits" property to Mod-N counter to change the number of output ports

## 2012-10-03  Koichi Akabe  <vbkaisetsu@gmail.com>

 split drawComponent functions for animation
 remove DummyComponent
 use signals instead of "parent" in some classes
 release version 2.5.1
 change the name from "timing chart" to "timing diagram"

## 2012-10-02  Koichi Akabe  <vbkaisetsu@gmail.com>

 release version 2.5
 update Japanese translation

## 2012-10-01  Koichi Akabe  <vbkaisetsu@gmail.com>

 update translation template
 remove unnecessary button
 add a cursor position spin to the top of the timing chart window

## 2012-09-30  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix behavior of unit combo boxes on the timing chat window
 fix bihavior of the cursor on the timing chart
 update NEWS
 add cursor to timing chart to toggle switches at specified time
 add initial state property for oscillator and switch
 update translation template
 update examples for new property

## 2012-09-28  Koichi Akabe  <vbkaisetsu@gmail.com>

 move essential attributes to BaseComponent

## 2012-09-27  Koichi Akabe  <vbkaisetsu@gmail.com>

 update NEWS
 prohibit moving components to out of range
 get cursor position on button press

## 2012-09-25  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix to break analysis when output port is short circuit

## 2012-08-13  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix incomplete change
 update NEWS
 force direction of nets started at a pin of a component

## 2012-07-04  Koichi Akabe  <vbkaisetsu@gmail.com>

 disable highlight while components are picked

## 2012-07-03  Koichi Akabe  <vbkaisetsu@gmail.com>

 add max calc iters and max calc duration preferences

## 2012-06-18  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix behaviour on drawing area
 bump to 2.3
 fix behaviour of oscillator
 fix property window of oscillator

## 2012-06-17  Koichi Akabe  <vbkaisetsu@gmail.com>

 add duration property for oscillator
 update example logic circuit
 update translation
 code cleanup
 remove unused variable
 fix behaviour on activate property
 fix bihavior on ctrl key is pressed
 code cleanup

## 2012-06-14  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix font name
 fix drawing chart

## 2012-06-11  Koichi Akabe  <vbkaisetsu@gmail.com>

 change default font to FreeMono 12pt

## 2012-05-27  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix drawing on AND and NAND components

## 2012-05-24  Koichi Akabe  <vbkaisetsu@gmail.com>

 update NEWS and INSTALL
 bump to 2.2
 fix behaviour on toggle net button
 update translation

## 2012-05-16  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix OR symbol on running mode
 fix translation
 add preference for symbols (MIL/ANSI, IEC)

## 2012-05-12  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix to apply color settings to nets on components
 add Preferences window
 add Preferences.py to Makefile.am
 add POTFILES.skip

## 2012-05-10  Koichi Akabe  <vbkaisetsu@gmail.com>

 manage fonts and colors in Preference class (for Preferences window)
 add value checking for Probe component
 replace install instruction with the default one
 remove non-required files

## 2012-05-08  Koichi Akabe  <vbkaisetsu@gmail.com>

 update TODO
 bump to 2.1
 change to use variables to get cursor positions
 add dist-hook to create ChangeLog automatically

## 2012-05-05  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix behavior on schematics area

## 2012-05-04  Koichi Akabe  <vbkaisetsu@gmail.com>

 add tooltips for component window
 add components' names on property window

## 2012-05-03  Koichi Akabe  <vbkaisetsu@gmail.com>

 show dialog when timing chart will be too wide
 add "Save chart" button for timing chart
 update text layout on components
 add "Save as image" menu for schematics

## 2012-05-02  Koichi Akabe  <vbkaisetsu@gmail.com>

 add new example: ocillators.glc
 add property's names on glc file to identify each properties
 (therefore it can't read old files)
 fix drawing graduation with wrong space
 change a message from "high frequency" to "infinite frequency"

## 2012-05-01  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix a bug on loading and saving files
 change to depend on Python3 on autotools
 update translation

## 2012-04-30  Koichi Akabe  <vbkaisetsu@gmail.com>

 fix minor bugs
 add graduation for timing chart
 add options to scale, to set drawing range and to redraw chart
 remove translation for units
 fix minor bugs
 cleanup codes

## 2012-04-27  Koichi Akabe  <koichi@localhost>

 manage delays in seconds and changed unit from "ns" to "µs"
 remove excutable bit
 update auto tools
 fix OR, XOR, NOR components on draw terminals
 use activate signal to apply properties
 change website's locations

## 2012-04-26  Koichi Akabe  <vbkaisetsu@gmail.com>

 initial commit (ported from wxlogic)
