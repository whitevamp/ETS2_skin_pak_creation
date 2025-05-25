def create_ui_mat(paint_id, folder):
    mat_path = folder / f"{paint_id}.mat"
    content = f"""effect : "ui.rfx" {{
	texture : "texture" {{
		source : "{paint_id}.tobj"
		u_address : clamp
		v_address : clamp
		mip_filter : none
	}}
}}"""
    with open(mat_path, "w") as f:
        f.write(content)
