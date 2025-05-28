using System.Collections.Generic;

namespace SkinPackCreator.Core.Models
{
    public enum VehicleType
    {
        Truck,
        TrailerOwned
    }

    public class VehicleDefinition
    {
        public string InternalName { get; } // Game's internal name
        public string DisplayName { get; }  // User-friendly name for UI
        public VehicleType Type { get; }

        public VehicleDefinition(string internalName, string displayName, VehicleType type)
        {
            InternalName = internalName;
            DisplayName = displayName;
            Type = type;
        }

        // Override ToString for easier display in UI elements if needed directly
        public override string ToString() => DisplayName;
    }

    public static class DefaultVehicles
    {
        public static List<VehicleDefinition> AllTrucks { get; } = new List<VehicleDefinition>
        {
            new VehicleDefinition("daf.2021", "DAF 2021", VehicleType.Truck),
            new VehicleDefinition("daf.xd", "DAF XD", VehicleType.Truck),
            new VehicleDefinition("daf.xf", "DAF XF", VehicleType.Truck),
            new VehicleDefinition("daf.xf_euro6", "DAF XF Euro 6", VehicleType.Truck),
            new VehicleDefinition("iveco.hiway", "Iveco Hi-Way", VehicleType.Truck),
            new VehicleDefinition("iveco.stralis", "Iveco Stralis", VehicleType.Truck),
            new VehicleDefinition("iveco.sway", "Iveco S-Way", VehicleType.Truck),
            new VehicleDefinition("man.tgx", "MAN TGX", VehicleType.Truck),
            new VehicleDefinition("man.tgx_2020", "MAN TGX 2020", VehicleType.Truck),
            new VehicleDefinition("man.tgx_euro6", "MAN TGX Euro 6", VehicleType.Truck),
            new VehicleDefinition("mercedes.actros", "Mercedes Actros", VehicleType.Truck),
            new VehicleDefinition("mercedes.actros2014", "Mercedes Actros 2014", VehicleType.Truck),
            // The original list had "mercedes.actros4". Assuming it's the same as actros2014 or a typo.
            // If it's distinct, it would need a different display name. For now, consolidated.
            new VehicleDefinition("mercedes.actros_mp2", "Mercedes Actros MP2", VehicleType.Truck),
            new VehicleDefinition("mercedes.actros_mp3", "Mercedes Actros MP3", VehicleType.Truck),
            new VehicleDefinition("ram.3500", "RAM 3500", VehicleType.Truck), // ATS truck
            new VehicleDefinition("renault.magnum", "Renault Magnum", VehicleType.Truck),
            new VehicleDefinition("renault.premium", "Renault Premium", VehicleType.Truck),
            new VehicleDefinition("renault.radiance", "Renault Radiance (Concept)", VehicleType.Truck),
            new VehicleDefinition("renault.t", "Renault T", VehicleType.Truck),
            new VehicleDefinition("scania.r", "Scania R", VehicleType.Truck),
            new VehicleDefinition("scania.r_2016", "Scania R 2016", VehicleType.Truck),
            new VehicleDefinition("scania.spectr", "Scania Spectr (Custom/Mod?)", VehicleType.Truck), // Might be a mod truck
            new VehicleDefinition("scania.streamline", "Scania Streamline", VehicleType.Truck),
            new VehicleDefinition("scania.s_2016", "Scania S 2016", VehicleType.Truck),
            new VehicleDefinition("tgenscania", "TGEN Scania (Mod?)", VehicleType.Truck), // Might be a mod truck
            new VehicleDefinition("volvo.fh16", "Volvo FH16", VehicleType.Truck),
            new VehicleDefinition("volvo.fh16_2012", "Volvo FH16 2012", VehicleType.Truck),
            new VehicleDefinition("volvo.fh_2021", "Volvo FH 2021", VehicleType.Truck),
            new VehicleDefinition("volvo.fh_2024", "Volvo FH 2024", VehicleType.Truck)
            // Add other trucks as needed, ensure display names are user-friendly
        };

        public static List<VehicleDefinition> AllTrailers { get; } = new List<VehicleDefinition>
        {
            new VehicleDefinition("feldbinder.eut", "Feldbinder EUT", VehicleType.TrailerOwned),
            new VehicleDefinition("feldbinder.kip", "Feldbinder KIP", VehicleType.TrailerOwned),
            new VehicleDefinition("feldbinder.tsaadr", "Feldbinder TSA ADR", VehicleType.TrailerOwned),
            new VehicleDefinition("feldbinder.tsalm", "Feldbinder TSA LM", VehicleType.TrailerOwned),
            new VehicleDefinition("freight.casca", "Freightliner Cascadia (Trailer?)", VehicleType.TrailerOwned), // Name seems like a truck
            new VehicleDefinition("freight.xl", "Freightliner XL (Trailer?)", VehicleType.TrailerOwned), // Name seems like a truck
            new VehicleDefinition("koegel.cargo", "Kögel Cargo", VehicleType.TrailerOwned),
            new VehicleDefinition("koegel.mega", "Kögel Mega", VehicleType.TrailerOwned),
            new VehicleDefinition("koegel.multi", "Kögel Multi", VehicleType.TrailerOwned),
            new VehicleDefinition("koegel.multi_mega", "Kögel Multi Mega", VehicleType.TrailerOwned),
            new VehicleDefinition("krone.coolliner", "Krone Cool Liner", VehicleType.TrailerOwned),
            new VehicleDefinition("krone.dryliner", "Krone Dry Liner", VehicleType.TrailerOwned),
            new VehicleDefinition("krone.paperliner", "Krone Paper Liner", VehicleType.TrailerOwned),
            new VehicleDefinition("krone.profiliner", "Krone Profi Liner", VehicleType.TrailerOwned),
            new VehicleDefinition("krone.profilinerbm", "Krone Profi Liner BM", VehicleType.TrailerOwned),
            new VehicleDefinition("krone.profilinerhd", "Krone Profi Liner HD", VehicleType.TrailerOwned),
            new VehicleDefinition("schwmuller.cisternfood", "Schmüller Food Cistern", VehicleType.TrailerOwned), // Schwmuller, not Schmüller
            new VehicleDefinition("schwmuller.curtain", "Schmüller Curtain", VehicleType.TrailerOwned),
            new VehicleDefinition("schwmuller.reefer", "Schmüller Reefer", VehicleType.TrailerOwned),
            new VehicleDefinition("scs.box", "SCS Box Trailer", VehicleType.TrailerOwned),
            new VehicleDefinition("scs.chemtank", "SCS Chemical Tank", VehicleType.TrailerOwned),
            new VehicleDefinition("scs.dumper", "SCS Dumper", VehicleType.TrailerOwned),
            new VehicleDefinition("scs.foodtank", "SCS Food Tank", VehicleType.TrailerOwned),
            new VehicleDefinition("scs.fueltank", "SCS Fuel Tank", VehicleType.TrailerOwned),
            new VehicleDefinition("scs.gastank", "SCS Gas Tank", VehicleType.TrailerOwned),
            new VehicleDefinition("scs.livestock", "SCS Livestock Trailer", VehicleType.TrailerOwned),
            new VehicleDefinition("scs.silo", "SCS Silo Trailer", VehicleType.TrailerOwned),
            new VehicleDefinition("tirsan.scs", "Tirsan SCS", VehicleType.TrailerOwned),
            new VehicleDefinition("tirsan.sks", "Tirsan SKS", VehicleType.TrailerOwned),
            new VehicleDefinition("tirsan.sri", "Tirsan SRI", VehicleType.TrailerOwned),
            new VehicleDefinition("wielton.bulkm", "Wielton Bulk Master", VehicleType.TrailerOwned),
            new VehicleDefinition("wielton.curtainm", "Wielton Curtain Master", VehicleType.TrailerOwned),
            new VehicleDefinition("wielton.dropsidem", "Wielton Dropside Master", VehicleType.TrailerOwned),
            new VehicleDefinition("wielton.drym", "Wielton Dry Master", VehicleType.TrailerOwned),
            new VehicleDefinition("wielton.strongm", "Wielton Strong Master", VehicleType.TrailerOwned),
            new VehicleDefinition("wielton.weightm", "Wielton Weight Master", VehicleType.TrailerOwned)
            // Add other trailers as needed
        };
    }
}
