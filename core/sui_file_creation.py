#from sii_file_creation import create_truck_sii, create_trailer_sii

def create_truck_sui(paint_id, path, model):
    # content = f"""# Mods Studio 2 mod template: Trailer skin

# name: "{paint_id}"
# price: 1
# unlock: 0
# icon: "{paint_id}"
# airbrush: true
# base_color_locked: true
# base_color: (0.600000, 0.600000, 0.600000)
# alternate_uvset: false
# """
    content = f"""# Mods Studio 2 mod template: Advanced truck skin (NextGen)

	name:					"{paint_id}"
	price:					1
	unlock:					0
	icon:					"{paint_id}"
	airbrush:				true
	base_color_locked:		true
	base_color:				(0.600000, 0.600000, 0.600000)
	alternate_uvset:		false
"""

    with open(path, "w") as f:
        f.write(content)
        
# def create_trailer_sui(paint_id, path, model):
    # content = f"""# Mods Studio 2 mod template: Trailer skin

# name: "{paint_id}"
# price: 1
# unlock: 0
# icon: "{paint_id}"
# airbrush: true
# base_color_locked: true
# base_color: (0.600000, 0.600000, 0.600000)
# alternate_uvset: false
# """

    # with open(path, "w") as f:
        # f.write(content)
        
def create_trailer_sui(paint_id, path, model):
    content = f"""# Mods Studio 2 mod template: Advanced truck skin (NextGen)

	name:					"{paint_id}"
	price:					1
	unlock:					0
	icon:					"{paint_id}"
	airbrush:				true
	base_color_locked:		true
	base_color:				(0.600000, 0.600000, 0.600000)
	alternate_uvset:		false
"""

    with open(path, "w") as f:
        f.write(content)