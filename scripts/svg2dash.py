import sys

def create_font_from_svg():
  try:
    import fontforge
    import psMat
  except ModuleNotFoundError:
    print(f"Usage: fontforge -script {sys.argv[0]} <input.svg>")
    print("(don't run this with python directly)")
    sys.exit(1)

  SVG_FILE = sys.argv[1]     
  OUTPUT_FILE = "Separator.ttf" 
  FONT_NAME = "Separator"     
  EM_SIZE = 1000        
  ASCENT = 800
  DESCENT = 200

  # 1. Create a new empty font
  font = fontforge.font()
  
  # 2. Set encoding to Unicode to support Em Dash (0x2014)
  font.encoding = 'UnicodeFull'
  
  font.fontname = FONT_NAME
  font.fullname = FONT_NAME
  font.familyname = FONT_NAME
  font.em = EM_SIZE
  font.ascent = ASCENT
  font.descent = DESCENT
  
  # 3. Define the target glyphs
  targets = [
    (0x2D, "hyphen"),   # Hyphen -
    (0x2013, "endash"),   # En Dash –
    (0x2014, "emdash")  # Em Dash —
  ]
  
  print(f"Processing {SVG_FILE}...")

  for code, name in targets:
    # Create the character slot
    glyph = font.createChar(code, name)
    glyph.clear()
    
    # Import SVG
    glyph.importOutlines(SVG_FILE)
    
    # Measure
    bbox = glyph.boundingBox()
    xmin, ymin, xmax, ymax = bbox
    initial_height = ymax - ymin
    
    if initial_height == 0:
      print(f"Warning: Glyph {name} has 0 height. Skipping.")
      continue

    # Transform
    trans_matrix = psMat.translate(-xmin, -ymin)
    glyph.transform(trans_matrix)
    
    # Scale
    scale_factor = EM_SIZE / initial_height
    scale_matrix = psMat.scale(scale_factor)
    glyph.transform(scale_matrix)
    
    # Vertical Center logic
    # Font center is midpoint of design space (300)
    target_center = (ASCENT - DESCENT) / 2
    
    new_bbox = glyph.boundingBox()
    glyph_height = new_bbox[3] - new_bbox[1]
    glyph_center_y = new_bbox[1] + (glyph_height / 2)
    
    shift_y = target_center - glyph_center_y
    move_matrix = psMat.translate(0, shift_y)
    glyph.transform(move_matrix)

    # Set Width
    final_bbox = glyph.boundingBox()
    new_width = final_bbox[2] - final_bbox[0]
    glyph.width = int(new_width)
    
    print(f" - Created {name} (U+{code:X}): Width {glyph.width}")

  font.generate(OUTPUT_FILE)
  print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(f"Usage: fontforge -script {sys.argv[0]} <input.svg>")
  else:
    create_font_from_svg()
