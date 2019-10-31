# Helper functions
def separateFirstWord(text, lowercaseFirst=True):
	space = text.find(" ")
	command = text
	arg = ""
	if space >= 0:
		command = text[0:space]
		arg = text[space+1:]
	if lowercaseFirst:
		command = command.lower()
	return (command, arg)

def parseNumber(number):
	if number in aliases:
		return parseNumber(aliases[number])
	if number.startswith("$"):
		return int(number[1:], 16)
	return int(number)

def parseTile(tile):
	""" Parse the nametable value for one tile """
	global default_palette, default_base
	value = default_base

	if tile.find(":") >= 0: # Base override
		split = tile.split(":")
		value = parseNumber(split[0])
		tile = split[1]

	if tile.endswith("_"): # No-op separator
		tile = tile[:-1]

	# Read the tile number in the format of x,y starting from the specified base
	if tile.find(",") >= 0:
		split = [parseNumber(s) for s in tile.split(",")]
		value += split[0]+split[1]*16
	else:
		value += parseNumber(tile)
	return value

# Globals
aliases = {}
default_palette = 0
default_base = 0
block = None
all_blocks = []

# Read and process the file
with open("blocks.txt") as f:
    text = [s.rstrip() for s in f.readlines()]

def saveBlock():
	if block == None:
		return
	all_blocks.append(block)

for line in text:
	if not len(line):
		continue
	if line.startswith("#"): # comment
		continue
	if line.startswith("+"): # new block
		saveBlock()
		# Reset to prepare for the new block
		block = {"name": line[1:], "solid": False, "solid_top": False, \
		  "tiles": [], "palette": default_palette}
		continue
	word, arg = separateFirstWord(line)
	# Miscellaneous directives
	if word == "alias":
		name, value = separateFirstWord(arg)
		aliases[name] = value

	# Tile info shared with several blocks
	elif word == "base":
		default_base = parseNumber(arg)
	elif word == "palette":
		default_palette = parseNumber(arg)

	# Specifying tiles and tile attributes
	elif word == "solid":
		block["solid"] = True
	elif word == "solid_top":
		block["solid_top"] = True
	elif word == "t": # add tiles
		split = arg.split(" ")
		for tile in split:
			block["tiles"].append(parseTile(tile))
	elif word == "q": # add four tiles at once
		tile = parseTile(arg)
		block["tiles"] = [tile, tile+1, tile+16, tile+17]

# Save the last one
saveBlock()

# Generate the output that's actually usable in the game
outfile = open("blockdata.z80", "w")
outfile.write('; This is automatically generated. Edit "blocks.txt" instead\n')
outfile.write("SECTION \"metatiledata\", ROM0\n")
outfile.write("Metatiles:\n")
for b in all_blocks:
	outfile.write('  db $%.2x, $%.2x, $%.2x, $%.2x ; %s\n' % (b['tiles'][0], b['tiles'][1], b['tiles'][2], b['tiles'][3], b['name']))

outfile.write('\nMetatileFlags:\n')
for b in all_blocks:
	outfile.write('  db %d ; %s\n' % (b['palette'] | (0xc0 * b['solid']) | (0x40 * b['solid_top']), b['name']))

outfile.close()

# Generate the enum in a separate file
outfile = open("blockenum.z80", "w")
outfile.write('; This is automatically generated. Edit "blocks.txt" instead\n')
outfile.write('  enum_start\n')
for b in all_blocks:
	outfile.write('  enum_elem BLOCK_%s\n' % b['name'])
outfile.close()
