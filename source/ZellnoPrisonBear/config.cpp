class CfgPatches
{
    class ZellnoPrisonBear
    {
        units[] =
        {
            "Animal_UrsusArctos_ZellnoPrison"
        };
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] =
        {
            "DZ_Animals_ursus_arctos"
        };
    };
};

class CfgVehicles
{
    class Animal_UrsusArctos;

    class Animal_UrsusArctos_ZellnoPrison : Animal_UrsusArctos
    {
        scope = 2;
        displayName = "Zellno Prison Bear";
        descriptionShort = "A resilient bear guarding the Prison Island Black Market.";

        class DamageSystem
        {
            class GlobalHealth
            {
                class Health
                {
                    hitpoints = 15000;
                };

                class Blood
                {
                    hitpoints = 50000;
                };

                class Shock
                {
                    hitpoints = 5000;
                };
            };
        };
    };
};
