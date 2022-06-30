shortcut_ui = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkShortcutsWindow" id="shortcuts">
    <property name="modal">1</property>
    <child>
      <object class="GtkShortcutsSection">
        <property name="section-name">editor</property>
        <property name="title" translatable="yes">Editor</property>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes">General</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Help</property>
                <property name="accelerator">F1</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">New Workspace</property>
                <property name="accelerator">&lt;ctrl&gt;N</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Open File</property>
                <property name="accelerator">&lt;ctrl&gt;o</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Save File</property>
                <property name="accelerator">&lt;ctrl&gt;s</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Quit</property>
                <property name="accelerator">&lt;ctrl&gt;Q</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Save file as</property>
                <property name="accelerator">&lt;ctrl&gt;&lt;shift&gt;s</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Keyboard Shortcuts</property>
                <property name="accelerator">&lt;ctrl&gt;&lt;shift&gt;question</property>
              </object>
            </child>
          </object>
        </child>
      </object>
    </child>
    <child>
      <object class="GtkShortcutsSection">
        <property name="section-name">components</property>
        <property name="title" translatable="yes">Editing</property>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes">Components</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Flip Component Horizontally</property>
                <property name="accelerator">H</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Flip Component Vertically</property>
                <property name="accelerator">V</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Rotate Component Right</property>
                <property name="accelerator">R</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Rotate Component Left</property>
                <property name="accelerator">L</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Edit component properties</property>
                <property name="accelerator">&lt;ctrl&gt;p</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Toggle net </property>
                <property name="accelerator">&lt;ctrl&gt;E</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Show timing diagram</property>
                <property name="accelerator">&lt;ctrl&gt;t</property>
              </object>
            </child>
          </object>
        </child>
      </object>
    </child>
    <child>
      <object class="GtkShortcutsSection">
        <property name="section-name">drawarea</property>
        <property name="title" translatable="yes">Workspace</property>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes">Workspace</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Undo</property>
                <property name="accelerator">&lt;ctrl&gt;z</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Copy</property>
                <property name="accelerator">&lt;ctrl&gt;c</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Cut</property>
                <property name="accelerator">&lt;ctrl&gt;x</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Paste</property>
                <property name="accelerator">&lt;ctrl&gt;v</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Redo </property>
                <property name="accelerator">&lt;ctrl&gt;&lt;shift&gt;z</property>
              </object>
            </child>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>
"""
menu_xml = """
    <?xml version="1.0" encoding="UTF-8"?>
    <interface>
        <menu id="app-menu">
            <section> 
                <item>
                    <attribute name="label">_New</attribute>
                    <attribute name="action">app.on_action_new_pressed</attribute>
                    <attribute name="accel">&lt;Ctrl&gt;N</attribute>
               </item>
                <item>
                    <attribute name="label">Open</attribute>
                    <attribute name="action">app.on_action_open_pressed</attribute>
                    <attribute name="accel">&lt;Ctrl&gt;O</attribute>
               </item>
            </section>
            <section>
                <item>
                    <attribute name="label">Save</attribute>
                    <attribute name="action">app.on_action_save_pressed</attribute>
                    <attribute name="accel">&lt;Ctrl&gt;S</attribute>
               </item>
                <item>
                    <attribute name="label">Save as</attribute>
                    <attribute name="action">app.on_action_saveas_pressed</attribute>
                    <attribute name="accel">&lt;Shift&gt;&lt;Ctrl&gt;S</attribute>
               </item>
                <item>
                    <attribute name="label">Save Image</attribute>
                    <attribute name="action">app.on_action_save_image</attribute>
               </item>
            </section>
            <section>
                <submenu>
                    <attribute name="label" translatable="yes">Help</attribute>
                    <section>
                        <item>
                            <attribute name="label">Content</attribute>
                            <attribute name="action">app.on_action_show_help</attribute>
                            <attribute name="accel">F1</attribute>
                           </item>
                            <item>
                               <attribute name="label">Report Issue</attribute>
                               <attribute name="action">app.on_action_bug_pressed</attribute>
                           </item>
                    </section>
                </submenu>
                <item>
                    <attribute name="label">Shortcuts</attribute>
                    <attribute name="action">app.on_show_shortcut</attribute>
                    <attribute name="accel">&lt;ctrl&gt;&lt;shift&gt;question</attribute>
               </item>
            </section>
            <section>
                <item>
                    <attribute name="label">Preference</attribute>
                    <attribute name="action">app.on_action_prefs_pressed</attribute>
               </item>
                <item>
                    <attribute name="label">About</attribute>
                    <attribute name="action">app.on_action_about_pressed</attribute>
               </item>
               <item>
                    <attribute name="label">Quit</attribute>
                    <attribute name="action">app.on_action_quit_pressed</attribute>
                    <attribute name="accel">&lt;Ctrl&gt;Q</attribute>
               </item>
            </section>
        </menu>
    </interface>"""
