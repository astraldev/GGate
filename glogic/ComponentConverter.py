# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from glogic.Components import comp_dict
from glogic.Utils import *
from glogic import const, config
from gettext import gettext as _
import copy

required = [2, 6] 
backward_compat = [0]

def components_to_string(components):
	str_data =  "version\n"
	str_data += " author=%s\n" % config.VERSION
	str_data += " required=%s\n\n" % ".".join([str(x) for x in required])

	for c in components:
		if c[0] == const.component_net:
			str_data += "net\n position=%d,%d,%d,%d\n\n" % (c[1], c[2], c[3], c[4])
		else:
			str_data += "%s\n" % c[0]
			str_data += " position=%d,%d\n" % (c[1].pos_x, c[1].pos_y)
			str_data += " input_level=%s\n" % ",".join([str(int(p)) for p in c[1].input_level])
			str_data += " output_level=%s\n" % ",".join([str(int(p)) for p in c[1].output_level])
			str_data += " matrix=%s\n" % ",".join([str(int(p)) for p in c[1].matrix])
			str_data += " properties=%s\n\n" % ",".join(["%s:%s" % (c[1].prop_names[i], encode_text(str(p))) for i, p in enumerate(c[1].values)])
	
	return str_data

def string_to_components(str_data):
	component = None
	components = []
	lines = str_data.split("\n")
	versioninfo = False
	for l in lines:
		l = l.strip()
		if l == "net":
			component = [const.component_net, 0, 10, 10, 10]
		elif l in comp_dict:
			component = [l, copy.deepcopy(comp_dict[l])]
		elif l == "version":
			versioninfo = True
			version_author = [0]
			version_required = [0]
		elif component is not None or versioninfo:
			if l == "":
				if versioninfo:
					this_version_str = config.VERSION.split(".")
					this_version = [int(x if x.isdigit() else 0) for x in this_version_str]
					m = len(version_required)
					n = len(this_version)
					if m > n:
						this_version += [0] * (m - n)
					for i, x in enumerate(version_required):
						if x > this_version[i]:
							return _("Compatibility error: This circuit requires glogic %s or later.") % ".".join([str(x) for x in version_required])
						elif x < this_version[i]:
							break
					m = len(backward_compat)
					n = len(version_author)
					if m > n:
						version_author += [0] * (m - n)
					for i, x in enumerate(backward_compat):
						if x > version_author[i]:
							return _("Compatibility error: This circuit was created by %(creator)s. glogic %(this)s doesn't support older than %(minimum)s.") % {"creator": ".".join([str(x) for x in version_author]), "this": config.VERSION, "minimum": ".".join([str(x) for x in backward_compat])}
						elif x < version_author[i]:
							break
					versioninfo = False
				else:
					components.append(component)
					component = None

			else:
				prop = l.split("=")
				if len(prop) == 2:
					if prop[0] == "position":
						p = prop[1].split(",")
						if component[0] == const.component_net:
							if len(p) == 4:
								component[1] = int(p[0])
								component[2] = int(p[1])
								component[3] = int(p[2])
								component[4] = int(p[3])
						else:
							if len(p) == 2:
								component[1].pos_x = int(p[0])
								component[1].pos_y = int(p[1])

					elif prop[0] == "input_level":
						if component[0] != const.component_net:
							p = prop[1].split(",")
							if len(component[1].input_level) == len(p):
								component[1].input_level = [bool(int(s if s.isdigit() else 0)) for s in p]

					elif prop[0] == "output_level":
						if component[0] != const.component_net:
							p = prop[1].split(",")
							if len(component[1].output_level) == len(p):
								component[1].output_level = [bool(int(s if s.isdigit() else 0)) for s in p]

					elif prop[0] == "matrix":
						if component[0] != const.component_net:
							p = prop[1].split(",")
							if len(p) == 4:
								component[1].matrix = [int(p[0]), int(p[1]), int(p[2]), int(p[3])]

					elif prop[0] == "properties":
						if component[0] != const.component_net:
							p = prop[1].split(",")
							p_pairs = [pp.split(":") for pp in p]
							i = 0
							for p in component[1].properties:
								if isinstance(p[1], tuple):
									if p[1][0] == const.property_select:
										for p_pair in p_pairs:
											if p_pair[0] == component[1].prop_names[i] and len(p_pair) == 2:
												component[1].values[i] = int(p_pair[1] if p_pair[1].isdigit() else 0)
												break
									elif p[1][0] == const.property_int:
										for p_pair in p_pairs:
											if p_pair[0] == component[1].prop_names[i] and len(p_pair) == 2:
												component[1].values[i] = int(p_pair[1] if p_pair[1].isdigit() else 0)
												break
									elif p[1][0] == const.property_float:
										try:
											for p_pair in p_pairs:
												if p_pair[0] == component[1].prop_names[i] and len(p_pair) == 2:
													component[1].values[i] = float(p_pair[1])
													break
										except ValueError:
											component[1].values[i] = 0.0
									else:
										for p_pair in p_pairs:
											if p_pair[0] == component[1].prop_names[i] and len(p_pair) == 2:
												component[1].values[i] = decode_text(p_pair[1])
												break
								elif p[1] == const.property_bool:
									for p_pair in p_pairs:
										if p_pair[0] == component[1].prop_names[i] and len(p_pair) == 2:
											component[1].values[i] = bool(int(p_pair[1] if p_pair[1].isdigit() else 0))
											break
								else:
									i -= 1
								i += 1
						component[1].propertyChanged(component[1].values)
						component[1].set_rot_props()

					elif versioninfo:
						if prop[0] == "author":
							version_author_str = prop[1].split(".")
							version_author = [int(x if x.isdigit() else 0) for x in version_author_str]
						elif prop[0] == "required":
							version_required_str = prop[1].split(".")
							version_required = [int(x if x.isdigit() else 0) for x in version_required_str]
	return components
