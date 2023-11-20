# Game Interfacing Settings
interface_settings = {
    'termination_key': 'F6',

    # Select the game here; can be full name, acronym, th## or just the game number.
    # Supported games: DDC, LoLK, UM, UDoALG
    # WIP Support: TD
    'game': 'No game selected'
}

# General Extraction Settings
extraction_settings = {

    # Name of an analysis class (e.g. 'AnalysisMostBulletsFrame') in analysis.py.
    # Sample analyses to get started and plot various entities can be found in analysis_examples.py.
    'analyzer': 'AnalysisTemplate',

    # Disable extraction of entities not required for your analysis to reduce lag
    'requires_bullets': True,
    'requires_enemies': True,
    'requires_items':   True,
    'requires_lasers':  True,
    'requires_screenshots': False,

    # See settings.md for more info
    'requires_max_curve_data': False,
    'requires_side2_pvp': True,
}

# Single-State Extraction Settings
# See settings.md for more info.
singlext_settings = {
    'show_untracked': False,
    'only_game_world': True,
    'show_enemy_drops': False,
    'list_print_limit': 30,
}

# Sequence Extraction Settings 
# See settings.md for more info.
seqext_settings = {
    'ingame_duration': '', #e.g. '520f', '12.4s', etc. or 'infinite', 'inf'
    'exact':        True,
    'auto_focus':   True,
    'auto_unpause': False,
    'auto_repause': True,
    'need_active':  False,
    'infinite_print_updates': True,
}

# Game-World Plotting Settings (Analysis)
# See settings.md for more info.
pyplot_settings = {
    'plot_scale':    1.0,
    'pyplot_factor': 0.2,
    'bullet_factor': 35,
    'enemy_factor':  5,
    'plot_laser_circles': True,
    'plot_enemy_hurtbox': False,
}

# ParaKit Script Settings
# See settings.md for more info.
parakit_settings = {
    'minimize_version_checker': False,
}
