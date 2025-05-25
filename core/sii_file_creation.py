#from sui_file_creation import create_truck_sui, create_trailer_sui


def create_truck_sii(paint_id, path, model):
    base_name = f"{paint_id}_0.{model}.paint_job"
    content = f"""SiiNunit
{{
accessory_paint_job_data: {base_name}
{{
@include "{paint_id}_shared.sui"
@include "{paint_id}_metallic.sui"
@include "{paint_id}_mask.sui"

suitable_for[]: "l2h1.{model}.cabin"
suitable_for[]: "l2h2.{model}.cabin"
suitable_for[]: "l2h3.{model}.cabin"
suitable_for[]: "l2h3_8x4.{model}.cabin"

paint_job_mask: "/vehicle/truck/upgrade/paintjob/{model}/{paint_id}/{paint_id}_0.tobj"
}}
}}"""

    with open(path, "w") as f:
        f.write(content)

def create_trailer_sii(paint_id, path, model):
    base_name = f"{paint_id}.{model}.paint_job"
    content = f"""SiiNunit
{{
# Created with Mods Studio 2 - the best tool to create ETS2 & ATS mods!
# Download for free from www.mods.studio

accessory_paint_job_data: {base_name}
{{

@include "{paint_id}_shared.sui"
@include "{paint_id}_metallic.sui"
@include "{paint_id}_mask.sui"

paint_job_mask: "/vehicle/trailer_owned/upgrade/paintjob/{model}/{paint_id}/{paint_id}_shared.tobj"

}}
}}"""

    with open(path, "w") as f:
        f.write(content)

#{trailer}