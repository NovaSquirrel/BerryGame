import json, glob, os

# -------------------------------------
# Parse the level JSON files
# -------------------------------------

RectRules = [
  {"T":"CHECKER",        "W":1,   "H":1,  "O": "db LVL_CHECKER, &P"},
  {"T":"SOLID",          "W":1,   "H":1,  "O": "db LVL_SOLID,   &P"},
  {"T":"DIRT",           "W":1,   "H":1,  "O": "db LVL_DIRT,    &P"},
  {"T":"PLAT",           "W":1,   "H":1,  "O": "db LVL_PLAT,    &P"},
  {"T":"FPLAT",          "W":1,   "H":1,  "O": "db LVL_FPLAT,   &P"},
  {"T":"LADDER",         "W":1,   "H":1,  "O": "db LVL_LADDER,  &P"},
  {"T":"FENCE",          "W":1,   "H":1,  "O": "db LVL_FENCE,   &P"},
  {"T":"GRASS",          "W":1,   "H":1,  "O": "db LVL_GRASS,   &P"},
  {"T":"FLOWER",         "W":1,   "H":1,  "O": "db LVL_FLOWER,  &P"},
  {"T":"WATER",          "W":1,   "H":1,  "O": "db LVL_WATER,   &P"},
  {"T":"SPRING",         "W":1,   "H":1,  "O": "db LVL_SPRING,  &P"},
  {"T":"POLE",           "W":1,   "H":1,  "O": "db LVL_POLE,    &P"},

  {"T":"CHECKER",        "W":16,  "H":1,  "O": "db LVL_H_CHECKER|&W, &P"},
  {"T":"CHECKER",        "W":1,   "H":16, "O": "db LVL_V_CHECKER|&H, &P"},

  {"T":"PLAT",           "W":16,  "H":1,  "O": "db LVL_H_PLAT|&W, &P"},
  {"T":"FPLAT",          "W":16,  "H":1,  "O": "db LVL_H_FPLAT|&W, &P"},
  {"T":"FENCE",          "W":16,  "H":1,  "O": "db LVL_H_FENCE|&W, &P"},
  {"T":"GRASS",          "W":16,  "H":1,  "O": "db LVL_H_GRASS|&W, &P"},
  {"T":"FLOWER",         "W":16,  "H":1,  "O": "db LVL_H_FLOWER|&W, &P"},
  {"T":"DIRT",           "W":16,  "H":1,  "O": "db LVL_H_DIRT|&W, &P"},

  {"T":"SOLID",          "W":16,  "H":1,  "O": "db LVL_H_SOLID|&W, &P"},
  {"T":"SOLID",          "W":1,   "H":16, "O": "db LVL_V_SOLID|&H, &P"},
  {"T":"LADDER",         "W":1,   "H":16, "O": "db LVL_V_LADDER|&H, &P"},

  {"T":"EMPTY",          "W":16,  "H":16, "O": "db LVL_RECT|LVL_EMPTY,   &P, &R"},
  {"T":"CHECKER",        "W":16,  "H":16, "O": "db LVL_RECT|LVL_CHECKER, &P, &R"},
  {"T":"SOLID",          "W":16,  "H":16, "O": "db LVL_RECT|LVL_SOLID,   &P, &R"},
  {"T":"DIRT",           "W":16,  "H":16, "O": "db LVL_RECT|LVL_DIRT,    &P, &R"},
  {"T":"PLAT",           "W":16,  "H":16, "O": "db LVL_RECT|LVL_PLAT,    &P, &R"},
  {"T":"FPLAT",          "W":16,  "H":16, "O": "db LVL_RECT|LVL_FPLAT,   &P, &R"},
  {"T":"LADDER",         "W":16,  "H":16, "O": "db LVL_RECT|LVL_LADDER,  &P, &R"},
  {"T":"FENCE",          "W":16,  "H":16, "O": "db LVL_RECT|LVL_FENCE,   &P, &R"},
  {"T":"GRASS",          "W":16,  "H":16, "O": "db LVL_RECT|LVL_GRASS,   &P, &R"},
  {"T":"FLOWER",         "W":16,  "H":16, "O": "db LVL_RECT|LVL_FLOWER,  &P, &R"},
  {"T":"WATER",          "W":16,  "H":16, "O": "db LVL_RECT|LVL_WATER,   &P, &R"},
  {"T":"SPRING",         "W":16,  "H":16, "O": "db LVL_RECT|LVL_SPRING,  &P, &R"},
  {"T":"POLE",           "W":16,  "H":16, "O": "db LVL_RECT|LVL_POLE,    &P, &R"},
];


class Rect(object):
	def __init__(self, j):
		self.type = j['Id']
		self.x = j['X']
		self.y = j['Y']
		self.w = j['W']
		self.h = j['H']
		self.xflip = 'XFlip' in j
		self.yflip = 'YFlip' in j
		self.extra = ''
		if 'Extra' in j:
			self.extra = j

	def __repr__(self):
		return '%s %d,%d %dx%d' % (self.type, self.x, self.y, self.w, self.h)

def convert_layer(layer):
	output = []

	# Process each rectangle
	for r in layer:
		if r.type == 'PLAYER':
			continue

		chosen_rule = None
		for rule in RectRules:
			if r.type != rule["T"]:
				continue
			if r.w > rule["W"]:
				continue
			if r.h > rule["H"]:
				continue
			chosen_rule = rule
			break
		assert chosen_rule != None

		out = chosen_rule["O"]
		out = out.replace("&P", str("$%.2x"  % ((r.y<<4)|r.x)))
		out = out.replace("&W", str(r.w-1))
		out = out.replace("&H", str(r.h-1))
		out = out.replace("&R", str("$%.2x"  % (((r.h-1)<<4)|(r.w-1))))
		output.append(out)
	return output

outfile = open("leveldata.z80", "w")
outfile.write('; This is automatically generated. Edit level JSON files instead\n')

for f in glob.glob("*.json"):
	plain_name = os.path.splitext(os.path.basename(f))[0]
	outfile.write("level_%s:\n" % plain_name)

	level_file = open(f)
	level_text = level_file.read()
	level_file.close()
	level_json = json.loads(level_text)

	num_layers = len(level_json["Layers"])
	assert num_layers == 1

	foreground = [Rect(x) for x in level_json["Layers"][0]["Data"]]

	# ---------------------------------
	# Find the player start position
	player_x, player_y = 5, 5
	for r in foreground:
		if r.type == 'PLAYER':
			player_x = r.x
			player_y = r.y

	# Write the foreground data. No header yet.
	fg_data = convert_layer(foreground)
	for line in fg_data:
		outfile.write("  %s\n" % line)
	outfile.write("  db LVL_DONE, $%.2x\n\n" % ((player_y<<4)|player_x))

outfile.close()
