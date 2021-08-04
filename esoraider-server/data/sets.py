from data.classes.general import BUFFS, DEBUFFS
from data.core import EsoEnum, GearSet


class GEAR_SETS(EsoEnum):
    PERFECTED_CRUSHING_WALL = GearSet(
        name='Perfected Crushing Wall',
        id=526,
        buffs=[BUFFS.CRUSHING_WALL.value],
        link='https://eso-hub.com/en/sets/perfected-crushing-wall',
        icon='https://eso-hub.com/storage/icons/gear_dwarvenscavenged_staff_a.png',
    )
    HARPOONERS_WADING_KILT = GearSet(
        name='Harpooner\'s Wading Kilt',
        id=594,
        buffs=[BUFFS.HUNTERS_FOCUS.value],
        link='https://eso-hub.com/en/sets/harpooners-wading-kilt',
        icon='https://eso-hub.com/storage/icons/gear_kothringikilt_a.png',
    )
    ELEMENTAL_CATALYST = GearSet(
        name='Elemental Catalyst',
        id=516,
        debuffs=[
            DEBUFFS.FROST_WEAKNESS.value,
            DEBUFFS.FLAME_WEAKNESS.value,
            DEBUFFS.SHOCK_WEAKNESS.value,
        ],
        link='https://eso-hub.com/en/sets/elemental-catalyst',
        icon='https://eso-hub.com/storage/icons/gear_northlandsalchlgt_head_a.png',
    )
    PERFECTED_CLAW_OF_YOLNAHKRIIN = GearSet(
        name='Perfected Claw of Yolnahkriin',
        id=451,
        buffs=[BUFFS.MINOR_COURAGE.value],
        link='https://eso-hub.com/en/sets/perfected-claw-of-yolnahkriin',
        icon='https://eso-hub.com/storage/icons/gear_sunspire_heavy_helmet_a.png',
    )
    ENCRATISS_BEHEMOTH = GearSet(
        name='Encratis\'s Behemoth',
        id=577,
        buffs=[BUFFS.BEHEMOTHS_AURA.value],
        link='https://eso-hub.com/en/sets/encratiss-behemoth',
        icon='https://eso-hub.com/storage/icons/gear_undfiregiant_head_a.png',
    )
    SPELL_POWER_CURE = GearSet(
        name='Spell Power Cure',
        id=185,
        buffs=[BUFFS.MAJOR_COURAGE.value],
        link='https://eso-hub.com/en/sets/spell-power-cure',
        icon='https://eso-hub.com/storage/icons/gear_imperialdaedric_light_head_a.png',
    )
    MASTER_ARCHITECT = GearSet(
        name='Master Architect',
        id=332,
        buffs=[BUFFS.MAJOR_SLAYER.value],
        link='https://eso-hub.com/en/sets/master-architect',
        icon='https://eso-hub.com/storage/icons/gear_clockwork_light_head_a.png',
    )
    SAXHLEEL_CHAMPION = GearSet(
        name='Saxhleel Champion',
        id=585,
        buffs=[BUFFS.MAJOR_FORCE_SAXHLEEL_CHAMPION.value],
        link='https://eso-hub.com/en/sets/saxhleel-champion',
        icon='https://eso-hub.com/storage/icons/gear_rockgrove_heavy_head_a.png',
    )
    PERFECTED_SAXHLEEL_CHAMPION = GearSet(
        name='Perfected Saxhleel Champion',
        id=589,
        buffs=[BUFFS.MAJOR_FORCE_SAXHLEEL_CHAMPION.value],
        link='https://eso-hub.com/en/sets/perfected-saxhleel-champion',
        icon='https://eso-hub.com/storage/icons/gear_rockgrove_heavy_head_a.png',
    )
    POWERFULL_ASSAULT = GearSet(
        name='Powerful Assault',
        id=180,
        buffs=[BUFFS.POWERFUL_ASSAULT.value],
        link='https://eso-hub.com/en/sets/powerful-assault',
        icon='https://eso-hub.com/storage/icons/gear_breton_medium_head_d.png',
    )
    WAY_OF_MARTIAL_KNOWLEDGE = GearSet(
        name='Way of Martial Knowledge',
        id=147,
        debuffs=[DEBUFFS.WAY_OF_MARTIAL_KNOWLEDGE.value],
        link='https://eso-hub.com/en/sets/way-of-martial-knowledge',
        icon='https://eso-hub.com/storage/icons/gear_yokudan_light_head_a.png',
    )
    # TODO: Track stacks somehow
    ZENS_REDRESS = GearSet(
        name='Z\'en\'s Redress',
        id=455,
        debuffs=[DEBUFFS.TOUCH_OF_ZEN.value],
        link='https://eso-hub.com/en/sets/zens-redress',
        icon='https://eso-hub.com/storage/icons/gear_stagzenlgt_helmet_a.png',
    )
    DIAMONDS_VICTORY = GearSet(
        name='Diamond\'s Victory',
        id=584,
        buffs=[BUFFS.MELEE_SUPREMACY.value, BUFFS.RANGE_SUPREMACY.value],
        link='https://eso-hub.com/en/sets/diamonds-victory',
        icon='https://eso-hub.com/storage/icons/gear_breton_light_head_d.png',
    )
    ROAR_OF_ALKOSH = GearSet(
        name='Roar of Alkosh',
        id=232,
        debuffs=[DEBUFFS.ROAR_OF_ALKOSH.value, DEBUFFS.LINE_BREAKER.value],
        link='https://eso-hub.com/en/sets/roar-of-alkosh',
        icon='https://eso-hub.com/storage/icons/gear_dromathra_medium_head_a.png',
    )
    WAR_MACHINE = GearSet(
        name='War Machine',
        id=331,
        buffs=[BUFFS.MAJOR_SLAYER.value],
        link='https://eso-hub.com/en/sets/war-machine',
        icon='https://eso-hub.com/storage/icons/gear_clockwork_medium_head_a.png',
    )
    PERFECTED_ROARING_OPPORTUNIST = GearSet(
        name='Perfected Roaring Opportunist',
        id=346,
        buffs=[BUFFS.MAJOR_SLAYER_ROARING_OPPORTUNIST.value],
        link='https://eso-hub.com/en/sets/perfected-roaring-opportunist',
        icon='https://eso-hub.com/storage/icons/gear_seagiantlgt_helmet.png',
    )
    PERFECTED_CAUSTIC_ARROW = GearSet(
        name='Perfected Caustic Arrow',
        id=531,
        buffs=[BUFFS.CAUSTIC_ARROW.value],
        link='https://eso-hub.com/en/sets/perfected-caustic-arrow',
        icon='https://eso-hub.com/storage/icons/gear_bosmer_bow_e.png',
    )
    PERFECTED_VIRULENT_SHOT = GearSet(
        name='Perfected Virulent Shot',
        id=426,
        buffs=[BUFFS.VIRULENT_SHOT.value],
        link='https://eso-hub.com/en/sets/perfected-virulent-shot',
        icon='https://eso-hub.com/storage/icons/gear_honorguard_bow_a.png',
    )
