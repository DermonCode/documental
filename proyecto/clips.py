# key -> (source, start s, end s). source = YouTube id, or 'steam_x' (src/steam_x.mp4 from steam.py)
# every range was checked by eye against what the narration says at that moment
CLIPS = {
 'ps5cine':  ('xm3VHjZl4DU', 172, 221),   # PS5 disc edition, cinematic close-ups
 'mpbox':    ('pEqgewp9DTc', 0, 40),      # 4K b-roll: boxed game in hand
 'mpdisc':   ('pEqgewp9DTc', 289, 330),   # 4K b-roll: game disc
 'shelf':    ('4iSpL_-hO8Y', 200, 280),   # 4K game room: shelves of carts and boxes
 'boxes':    ('4iSpL_-hO8Y', 450, 510),   # 4K game room: boxed N64 games
 'cifaldi1': ('ChqUlJdFYS8', 80, 98),     # Frank Cifaldi
 'cifaldi2': ('ChqUlJdFYS8', 289, 293.9),     # Cifaldi talking to camera
 'thecrew':  ('sZYruMkZazQ', 76, 118),    # The Crew, the game that started Stop Killing Games
 'aislop1':  ('9tgVqe0c8ps', 444, 459.5),   # AI-generated games (no commentator on screen)
 'aislop2':  ('9tgVqe0c8ps', 640, 655),
 'aislop3':  ('9tgVqe0c8ps', 388, 397.5),   # Steam publisher page full of AI games
 'spidey1':  ('steam_spideyrev', 9.5, 21),
 'spidey2':  ('steam_spideyrev', 21.5, 33.5),
 'shoulder1':('steam_acs', 36.8, 42.8),     # over-the-shoulder
 'shoulder2':('steam_horizon', 31, 36),
 'walk':     ('steam_acs', 62, 68.5),     # slow walk
 'unitymap': ('kt0M-FZV3RM', 96, 118),    # AC Unity map covered in icons
 'tga':      ('JvW-rDG5Jwc', 196, 204),   # The Game Awards 2025, Game of the Year
 'gotywin':  ('WDraAxp-Wp8', 11, 46),     # Sandfall team celebrating
 'gotystage':('WDraAxp-Wp8', 69, 100),    # team on stage with the award
 'clair':    ('steam_clair', 44, 72),
 'claircine':('steam_clair', 5, 16),
 'silksong': ('steam_silksong', 28, 64),
 'schedule': ('steam_schedule', 7.8, 52),
 'repo':     ('steam_repo', 57.5, 69.5),
 'sm64':     ('zA0v6lGYUEI', 318, 347),   # Mario 64 PC port
 'sm64rt':   ('zA0v6lGYUEI', 376, 416),   # Mario 64 ray tracing
 'soh':      ('AW_5Q_RyDhY', 228, 340),   # Ship of Harkinian
 'mm2s':     ('zA0v6lGYUEI', 159, 192),   # Majora: recomp vs 2 Ship 2 Harkinian (labelled)
 'pd':       ('zA0v6lGYUEI', 71, 90),     # Perfect Dark
 'sf64':     ('zA0v6lGYUEI', 49, 61.6),     # Starship (Star Fox 64)
 'mk64':     ('zA0v6lGYUEI', 99, 122.2),    # SpaghettiKart (Mario Kart 64)
 'jak':      ('IS4-l8RxCfo', 121, 220),   # OpenGOAL half of the comparison
 're3':      ('ZJ9Ee9XgK3k', 9, 65),
 'melee':    ('qfEWsZIhF9s', 36, 170),
 'sbk2':     ('ryzRqtZgjxA', 282, 376),
 'mmrecomp': ('xGZ5aHmUWic', 968, 1240),  # Zelda 64: Recompiled, ultrawide
 'duke':     ('zA0v6lGYUEI', 5, 22),
 'drmario':  ('zA0v6lGYUEI', 197, 211),
 'banjo':    ('zA0v6lGYUEI', 431.8, 457),
 'dino':     ('zA0v6lGYUEI', 290, 313.4),
 'sonic':    ('nEW-SFOjeCM', 11, 145),
 'skyhud':   ('PvP5KPtSKqQ', 1014.5, 1030), # Skyrim with the Minecraft HUD
 'skyplace': ('PvP5KPtSKqQ', 240, 285),   # placing blocks
 'skyplace2':('zRT3MyFwgu0', 236, 250),
 'skydig':   ('ZehgImMhnRY', 302, 325),   # digging into the terrain
 'skydig2':  ('ZehgImMhnRY', 625, 655),
 'skyfight': ('ZehgImMhnRY', 286, 298),   # fighting NPCs with Minecraft weapons
 'skyfight2':('zRT3MyFwgu0', 394, 407),
 'guidehow': ('MG1PxonJ158', 31, 39.3),     # "Game A draws the world / Game B: movement, blocks, combat"
 'guideask': ('MG1PxonJ158', 159, 170),   # prompt: clone SkyCraft and read it
 'guidelog': ('MG1PxonJ158', 221, 256),   # test, paste logs, repeat
 'fallout':  ('6QzpzfGrk-A', 104, 118),
 'fallout2': ('6QzpzfGrk-A', 45, 58),
 'wow':      ('sX3lsLiPS2s', 27, 45),
 'wow2':     ('sX3lsLiPS2s', 63, 81),
 'skate':    ('EaOnLVPKiPc', 4, 31),
 'doom':     ('hYSPaI5h4vQ', 16, 49),
}
