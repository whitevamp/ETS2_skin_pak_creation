import os # Making folders and renaming files
import shutil # Copying files
import binascii # Hex-ifying strings for TOBJ files
import codecs # Encoding TOBJ files
import configparser # Reading vehicle database files

class Vehicle:
    def __init__(self, file_name, game):
        veh_ini = configparser.ConfigParser(allow_no_value = True)
        veh_ini.read("library/vehicles/{}/{}".format(game, file_name), encoding="utf-8")
        self.path = veh_ini["vehicle info"]["vehicle path"]
        self.alt_uvset = veh_ini["vehicle info"].getboolean("alt uvset")
        self.display_name = veh_ini["vehicle info"]["name"]
        self.name = strip_diacritics(self.display_name)
        self.trailer = veh_ini["vehicle info"].getboolean("trailer")
        self.mod = veh_ini["vehicle info"].getboolean("mod")
        if self.mod:
            self.display_author = veh_ini["vehicle info"]["mod author"]
        else:
            self.display_author = "SCS"
        self.mod_author = strip_diacritics(self.display_author)
        self.mod_link_workshop = veh_ini["vehicle info"]["mod link workshop"]
        self.mod_link_forums = veh_ini["vehicle info"]["mod link forums"]
        self.mod_link_trucky = veh_ini["vehicle info"]["mod link trucky"]
        self.mod_link_author_site = veh_ini["vehicle info"]["mod link author site"]
        self.uses_accessories = veh_ini["vehicle info"].getboolean("uses accessories")
        self.bus_mod = veh_ini["vehicle info"].getboolean("bus mod")
        self.bus_door_workaround = veh_ini["vehicle info"].getboolean("bus door workaround")
        if self.uses_accessories:
            self.accessories = veh_ini["vehicle info"]["accessories"].split(";")
            self.acc_dict = {}
            for acc in self.accessories:
                if acc != "":
                    self.acc_dict[acc] = list(veh_ini[acc].keys())
        if self.trailer:
            self.separate_paintjobs = False
            self.type = "trailer_owned"
        else:
            self.separate_paintjobs = veh_ini["cabins"].getboolean("separate paintjobs")
            self.type = "truck"
            self.cabins = dict(veh_ini["cabins"].items())
            self.cabins.pop("separate paintjobs", None)
            for cabin in self.cabins:
                self.cabins[cabin] = self.cabins[cabin].split(";")
        # The canonical mod link is chosen with the priority of Steam Workshop > SCS Forums > Trucky Mod Hub > Mod author's own site
        if self.mod_link_workshop != "":
            self.mod_link = self.mod_link_workshop
        elif self.mod_link_forums != "":
            self.mod_link = self.mod_link_forums
        elif self.mod_link_trucky != "":
            self.mod_link = self.mod_link_trucky
        else:
            self.mod_link = self.mod_link_author_site



def make_folder(output_path, path):
    if not os.path.exists(output_path + "/" + path):
        os.makedirs(output_path + "/" + path)

def convert_string_to_hex(string_input):
    if isinstance(string_input, int):
        string_input = bytes([string_input])
    elif isinstance(string_input, str):
        string_input = string_input.encode()
    string_output = binascii.hexlify(string_input)
    string_output = string_output.decode()
    return string_output

def strip_diacritics(string_input):
    # unidecode is the standard way to normalise text, but it's licensed under GPL
    # More accurate replacements (e.g. ü to ue in German) are not universal, so diacritics are just stripped
    ascii_string = string_input.replace("\u00dc", "U") # Ü
    ascii_string = ascii_string.replace("\u00e4", "a") # ä
    ascii_string = ascii_string.replace("\u00e9", "e") # é
    ascii_string = ascii_string.replace("\u00f6", "o") # ö
    ascii_string = ascii_string.replace("\u00fc", "u") # ü
    return ascii_string

def check_if_ascii(string_input):
    ascii_string = string_input.encode("ascii", errors="ignore").decode()
    if string_input == ascii_string:
        return True
    else:
        return False

def contains_illegal_characters_sii(string_input):
    illegal_characters = ["\\","/","\""]
    any_found = False
    for char in illegal_characters:
        if char in string_input:
            any_found = True
    return any_found

def contains_illegal_characters_file_name(string_input):
    illegal_characters = ["<",">",":","\"","/","\\","|","?","*"]
    any_found = False
    for char in illegal_characters:
        if char in string_input:
            any_found = True
    return any_found

def contains_reserved_file_name(string_input):
    reserved_names = ["CON","PRN","AUX","NUL"]
    for i in range(9):
        reserved_names.append("COM" + str(i+1))
        reserved_names.append("LPT" + str(i+1))
    any_found = False
    for word in reserved_names:
        if string_input.upper() == word:
            any_found = True
    return any_found

def generate_tobj(path):
    tobj_string = "010AB170000000000000000000000000000000000100020002000303030002020001000000010000"
    tobj_string += convert_string_to_hex(len(path))
    tobj_string += "00000000000000"
    tobj_string += convert_string_to_hex(path)
    tobj_file = codecs.decode(tobj_string, "hex_codec")
    return tobj_file



# Loose files

def make_manifest_sii(output_path, mod_version, mod_name, mod_author, workshop_upload):
    file = open(output_path + "/manifest.sii", "w", encoding="utf-8")
    file.write("SiiNunit\n")
    file.write("{\n")
    file.write("mod_package: .package_name\n")
    file.write("{\n")
    file.write("\tpackage_version: \"{}\"\n".format(mod_version))
    if not workshop_upload:
        file.write("\tdisplay_name: \"{}\"\n".format(mod_name))
    file.write("\tauthor: \"{}\"\n".format(mod_author))
    file.write("\n")
    file.write("\tcategory[]: \"paint_job\"\n")
    file.write("\n")
    file.write("\ticon: \"Mod_Manager_Image.jpg\"\n")
    file.write("\tdescription_file: \"Mod_Manager_Description.txt\"\n")
    file.write("}\n")
    file.write("}\n")
    file.close()

def copy_mod_manager_image(output_path):
    shutil.copyfile("library/placeholder-files/mod-manager.jpg", output_path + "/Mod_Manager_Image.jpg")

def make_description(output_path, truck_list, truck_mod_list, bus_mod_list, trailer_list, trailer_mod_list, num_of_paintjobs):
    file = open(output_path + "/Mod_Manager_Description.txt", "w", encoding="utf-8")
    if num_of_paintjobs == "single":
        for veh in truck_list + trailer_list:
            file.write("This paint job supports the {}\n".format(veh.display_name))
        for veh in truck_mod_list + trailer_mod_list + bus_mod_list:
            file.write("This paint job supports {}'s {}\n".format(veh.display_author, veh.display_name.split(" [")[0]))
    else:
        if len(truck_list) + len(truck_mod_list) > 0:
            file.write("Trucks supported:\n")
            for veh in truck_list:
                file.write("- " + veh.display_name + "\n")
            for veh in truck_mod_list:
                file.write("- {}'s {}\n".format(veh.display_author, veh.display_name.split(" [")[0]))
            file.write("\n")
        if len(bus_mod_list) > 0:
            file.write("Buses supported:\n")
            for veh in bus_mod_list:
                file.write("- {}'s {}\n".format(veh.display_author, veh.display_name.split(" [")[0]))
            file.write("\n")
        if len(trailer_list) + len(trailer_mod_list) > 0:
            file.write("Trailers supported:\n")
            for veh in trailer_list:
                file.write("- " + veh.display_name + "\n")
            for veh in trailer_mod_list:
                file.write("- {}'s {}\n".format(veh.display_author, veh.display_name.split(" [")[0]))
    file.close()

def copy_versions_sii(output_path):
    shutil.copyfile("library/placeholder-files/versions.sii", output_path + "/versions.sii")

def copy_workshop_image(output_path):
    shutil.copyfile("library/placeholder-files/workshop.jpg", output_path + "/Workshop image.jpg")



# material folder

def make_material_folder(output_path):
    make_folder(output_path, "material/ui/accessory/")

def copy_paintjob_icon(output_path, ingame_name):
    shutil.copyfile("library/placeholder-files/icon.dds", output_path + "/material/ui/accessory/{} Icon.dds".format(ingame_name))

def make_paintjob_icon_tobj(output_path, ingame_name):
    file = open(output_path + "/material/ui/accessory/{} Icon.tobj".format(ingame_name), "wb")
    file.write(generate_tobj("/material/ui/accessory/{} Icon.dds".format(ingame_name)))
    file.close()

def make_paintjob_icon_mat(output_path, internal_name, ingame_name):
    file = open(output_path + "/material/ui/accessory/{}_icon.mat".format(internal_name), "w")
    file.write("material: \"ui\"\n")
    file.write("{\n")
    file.write("\ttexture: \"{} Icon.tobj\"\n".format(ingame_name))
    file.write("\ttexture_name: \"texture\"\n")
    file.write("}\n")
    file.close()



# def folder

def make_def_folder(output_path, veh):
    extra_path = ""
    if veh.uses_accessories:
        extra_path = "/accessory"
    make_folder(output_path, "def/vehicle/{}/{}/paint_job{}".format(veh.type, veh.path, extra_path))

def make_def_sii(output_path, veh, paintjob_name, internal_name, one_paintjob, ingame_name, main_dds_name, cab_internal_name=None):
    file = open(output_path + "/def/vehicle/{}/{}/paint_job/{}.sii".format(veh.type, veh.path, paintjob_name), "w", encoding="utf-8")
    file.write("SiiNunit\n")
    file.write("{\n")
    file.write("accessory_paint_job_data: {}.{}.paint_job\n".format(paintjob_name, veh.path))
    file.write("{\n")
    file.write("@include \"{}_settings.sui\"\n".format(internal_name))
    if not one_paintjob:
        if type(cab_internal_name) is list:
            for each_internal_name in cab_internal_name:
                file.write("\tsuitable_for[]: \"{}.{}.cabin\"\n".format(each_internal_name, veh.path))
        else:
            file.write("\tsuitable_for[]: \"{}.{}.cabin\"\n".format(cab_internal_name, veh.path))
    if veh.mod:
        file.write("\tpaint_job_mask: \"/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.tobj\"\n".format(veh.type, ingame_name, veh.name, veh.mod_author, main_dds_name))
    else:
        file.write("\tpaint_job_mask: \"/vehicle/{}/upgrade/paintjob/{}/{}/{}.tobj\"\n".format(veh.type, ingame_name, veh.name, main_dds_name))
    file.write("}\n")
    file.write("}\n")
    file.close()

def make_settings_sui(output_path, veh, internal_name, ingame_name, ingame_price, unlock_level):
    file = open(output_path + "/def/vehicle/{}/{}/paint_job/{}_settings.sui".format(veh.type, veh.path, internal_name), "w", encoding="utf-8")
    file.write("\tname: \"{}\"\n".format(ingame_name))
    file.write("\tprice: {}\n".format(ingame_price))
    file.write("\tunlock: {}\n".format(unlock_level))
    file.write("\tairbrush: true\n")
    file.write("\ticon: \"{}_icon\"\n".format(internal_name))
    if veh.bus_door_workaround: # Workaround for the weirdness surrounding bus mods' doors
        file.write("\tbase_color_locked: false\n")
    if veh.alt_uvset:
        file.write("\talternate_uvset: true\n")
    file.close()

def make_accessory_sii(output_path, veh, ingame_name, paintjob_name):
    file = open(output_path + "/def/vehicle/{}/{}/paint_job/accessory/{}.sii".format(veh.type, veh.path, paintjob_name), "w", encoding="utf-8")
    file.write("SiiNunit\n")
    file.write("{\n")
    ovr_counter = 0
    for acc_name in veh.acc_dict:
        file.write("\n")
        file.write("simple_paint_job_data: .ovr{}\n".format(ovr_counter))
        file.write("{\n")
        if veh.mod:
            file.write("\tpaint_job_mask: \"/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.tobj\"\n".format(veh.type, ingame_name, veh.name, veh.mod_author, acc_name))
        else:
            file.write("\tpaint_job_mask: \"/vehicle/{}/upgrade/paintjob/{}/{}/{}.tobj\"\n".format(veh.type, ingame_name, veh.name, acc_name))
        for acc in veh.acc_dict[acc_name]:
            file.write("\tacc_list[]: \"{}\"\n".format(acc))
        file.write("}\n")
        ovr_counter += 1
    file.write("}\n")
    file.close()



# vehicle folder

def make_vehicle_folder(output_path, veh, ingame_name):
    if veh.mod:
        make_folder(output_path, "vehicle/{}/upgrade/paintjob/{}/{} [{}]".format(veh.type, ingame_name, veh.name, veh.mod_author))
    else:
        make_folder(output_path, "vehicle/{}/upgrade/paintjob/{}/{}".format(veh.type, ingame_name, veh.name))

def copy_main_dds(output_path, veh, ingame_name, main_dds_name, template_zip):
    copy_square = False

    try:
        if template_zip != None:
            if main_dds_name+".dds" in template_zip.namelist():
                if veh.mod:
                    template_zip.extract(main_dds_name+".dds", output_path+"/vehicle/{}/upgrade/paintjob/{}/{} [{}]".format(veh.type, ingame_name, veh.name, veh.mod_author))
                else:
                    template_zip.extract(main_dds_name+".dds", output_path+"/vehicle/{}/upgrade/paintjob/{}/{}".format(veh.type, ingame_name, veh.name))
            elif veh.type == "truck": # Largest cabin only paint jobs
                if veh.alt_uvset:
                    largest_cabin_name = veh.cabins["a"][0][:-1]+", alt uvset).dds"
                else:
                    largest_cabin_name = veh.cabins["a"][0]+".dds"
                if veh.mod:
                    template_zip.extract(largest_cabin_name, output_path+"/vehicle/{}/upgrade/paintjob/{}/{} [{}]".format(veh.type, ingame_name, veh.name, veh.mod_author))
                    os.rename(output_path+"/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}".format(veh.type, ingame_name, veh.name, veh.mod_author, largest_cabin_name), output_path+"/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.dds".format(veh.type, ingame_name, veh.name, veh.mod_author, main_dds_name))
                else:
                    template_zip.extract(largest_cabin_name, output_path+"/vehicle/{}/upgrade/paintjob/{}/{}".format(veh.type, ingame_name, veh.name))
                    os.rename(output_path+"/vehicle/{}/upgrade/paintjob/{}/{}/{}".format(veh.type, ingame_name, veh.name, largest_cabin_name), output_path+"/vehicle/{}/upgrade/paintjob/{}/{}/{}.dds".format(veh.type, ingame_name, veh.name, main_dds_name))
            else:
                copy_square = True
        else:
            copy_square = True
    except KeyError:
        copy_square = True

    if copy_square:
        if veh.mod:
            shutil.copyfile("library/placeholder-files/empty.dds", output_path + "/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.dds".format(veh.type, ingame_name, veh.name, veh.mod_author, main_dds_name))
        else:
            shutil.copyfile("library/placeholder-files/empty.dds", output_path + "/vehicle/{}/upgrade/paintjob/{}/{}/{}.dds".format(veh.type, ingame_name, veh.name, main_dds_name))

def copy_accessory_dds(output_path, veh, ingame_name, game, template_zip):
    for acc_name in veh.acc_dict:
        copy_square = False

        if template_zip != None:
            if acc_name+".dds" in template_zip.namelist():
                if veh.mod:
                    template_zip.extract(acc_name+".dds", output_path+"/vehicle/{}/upgrade/paintjob/{}/{} [{}]".format(veh.type, ingame_name, veh.name, veh.mod_author))
                else:
                    template_zip.extract(acc_name+".dds", output_path+"/vehicle/{}/upgrade/paintjob/{}/{}".format(veh.type, ingame_name, veh.name))
            else:
                copy_square = True
        else:
            copy_square = True

        if copy_square:
            if veh.mod:
                shutil.copyfile("library/placeholder-files/empty.dds", output_path + "/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.dds".format(veh.type, ingame_name, veh.name, veh.mod_author, acc_name))
            else:
                shutil.copyfile("library/placeholder-files/empty.dds", output_path + "/vehicle/{}/upgrade/paintjob/{}/{}/{}.dds".format(veh.type, ingame_name, veh.name, acc_name))

def make_main_tobj(output_path, veh, ingame_name, main_dds_name):
    if veh.mod:
        file = open(output_path + "/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.tobj".format(veh.type, ingame_name, veh.name, veh.mod_author, main_dds_name), "wb")
        file.write(generate_tobj("/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.dds".format(veh.type, ingame_name, veh.name, veh.mod_author, main_dds_name)))
    else:
        file = open(output_path + "/vehicle/{}/upgrade/paintjob/{}/{}/{}.tobj".format(veh.type, ingame_name, veh.name, main_dds_name), "wb")
        file.write(generate_tobj("/vehicle/{}/upgrade/paintjob/{}/{}/{}.dds".format(veh.type, ingame_name, veh.name, main_dds_name)))
    file.close()

def make_accessory_tobj(output_path, veh, ingame_name):
    for acc_name in veh.acc_dict:
        if veh.mod:
            file = open(output_path + "/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.tobj".format(veh.type, ingame_name, veh.name, veh.mod_author, acc_name), "wb")
            file.write(generate_tobj("/vehicle/{}/upgrade/paintjob/{}/{} [{}]/{}.dds".format(veh.type, ingame_name, veh.name, veh.mod_author, acc_name)))
        else:
            file = open(output_path + "/vehicle/{}/upgrade/paintjob/{}/{}/{}.tobj".format(veh.type, ingame_name, veh.name, acc_name), "wb")
            file.write(generate_tobj("/vehicle/{}/upgrade/paintjob/{}/{}/{}.dds".format(veh.type, ingame_name, veh.name, acc_name)))
        file.close()

if __name__ == "__main__":
    print("Run \"packer.py\" to launch Paintjob Packer")
    print("")
    input("Press enter to quit")
