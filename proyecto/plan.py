# visual anchors: line substring -> clip keys from clips.py (cycled, ~6 s each, until the next anchor)
# each line shows what it talks about; graphics for specific lines are in build.py (G)
ANCHORS = [
 # cold open
 ("For most of this medium", ['mpbox']),
 ("A cartridge. A disc.", ['shelf']),
 ("That's ending.", ['ps5cine']),
 ("And honestly?", ['ps5cine']),
 ("Three years earlier", ['shelf']),
 ("How many could you still buy", ['boxes']),
 ("So if the industry isn't keeping", ['shelf']),
 ("This is the story of the people", ['mpdisc']),
 # I. the bad news
 ("Let's get the bad news", ['ps5cine']),
 ("Frank Cifaldi, who runs", ['cifaldi1']),
 ("His answer:", ['cifaldi2']),
 ("Players tried the legal route", ['thecrew']),
 ("And AI was flooding Steam", ['steam']),
 ("In 2024, about 11%", ['aislop1']),
 ("No discs.", ['aislop3']),
 ("Sounds hopeless, right?", ['aislop2']),
 ("It isn't.", ['claircine']),
 # II. giants and small teams
 ("a leak from Insomniac", ['spidey1']),
 ("When a game costs that much", ['spidey2']),
 ("So you get the same game", ['shoulder2']),
 ("Over-the-shoulder camera.", ['shoulder1']),
 ("Slow cinematic walks.", ['walk']),
 ("A map full of icons.", ['unitymap']),
 ("Then, at The Game Awards 2025", ['tga', 'gotywin']),
 ("Made for under 10 million", ['gotystage']),
 ("Hideo Kojima put it best.", ['gotystage']),
 ("Hollow Knight: Silksong sold", ['silksong']),
 ("Schedule I and R.E.P.O.", ['schedule', 'repo']),
 ("The games everyone was talking about", ['clair']),
 ("And some of the most exciting", ['boxes']),
 ("They're old games", ['sm64']),
 # III. decompilation
 ("In 2019, fans finished", ['sm64']),
 ("And once you have the code", ['sm64']),
 ("Mario 64 got a native PC port", ['sm64rt']),
 ("Ocarina of Time became", ['soh']),
 ("Majora's Mask followed", ['mm2s']),
 ("Perfect Dark.", ['pd']),
 ("Star Fox 64.", ['sf64']),
 ("Mario Kart 64.", ['mk64']),
 ("All rebuilt, all running", ['soh', 'mk64']),
 ("And it's not just Nintendo.", ['jak']),
 ("Publishers didn't love this.", ['re3']),
 ("But it didn't stop.", ['re3']),
 ("On September 8th, 2026", ['melee']),
 ("One developer working on Snowboard", ['sbk2']),
 # IV. static recompilation
 ("But what if you didn't have to rebuild", ['mmrecomp']),
 ("So the floodgates opened.", ['duke']),
 ("Dr. Mario 64.", ['drmario']),
 ("Banjo-Kazooie.", ['banjo']),
 ("Even Dinosaur Planet", ['dino']),
 ("Then, in March 2025", ['sonic']),
 ("None of these include the game", ['boxes']),
 ("You bring your own copy.", ['mpbox']),
 ("They just make sure it keeps", ['sonic']),
 # V. passthrough mods
 ("And then, at the end of September", ['skyhud']),
 ("In SkyCraft, you play Skyrim", ['skyhud']),
 ("You break and place blocks", ['skyplace', 'skyplace2']),
 ("You dig straight into", ['skydig', 'skydig2']),
 ("You fight its NPCs", ['skyfight', 'skyfight2']),
 ("And here's the crazy part.", ['skyhud']),
 ("Neither game was rewritten.", ['skyplace2']),
 ("Both run at the same time.", ['skyhud']),
 ("Skyrim draws everything", ['guidehow', 'skyplace']),
 ("People called it a passthrough", ['skyplace']),
 ("And within days", ['fallout2', 'wow2']),
 ("Minecraft in Fallout 4.", ['fallout']),
 ("Minecraft in World of Warcraft.", ['wow']),
 ("Skate 3 in GTA San Andreas.", ['skate']),
 ("DOOM in Skyrim.", ['doom']),
 ("Most of them were built with AI.", ['guideask']),
 ("You point an agent", ['guideask', 'guidelog']),
 ("Not long ago, this took years", ['guidelog']),
 ("Now it takes an idea", ['skate']),
 # epilogue
 ("So where does that leave us?", ['ps5cine']),
 ("The discs are going away", ['mpdisc', 'boxes']),
 ("But Mario 64's code is out there.", ['sm64rt']),
 ("Majora's Mask runs natively", ['mmrecomp']),
 ("Melee is fully decompiled.", ['melee']),
 ("And somebody put Minecraft", ['skydig']),
 ("Not because a publisher", ['shelf']),
 ("Because players did.", ['soh']),
 ("So play the games", ['silksong', 'clair']),
 ("Support the people preserving", ['cifaldi1']),
 ("And keep an eye on the small", ['schedule']),
 ("Most of what they make", ['repo']),
 ("But some of it will be", ['gotywin']),
 ("And this time, hopefully", ['shelf']),
 ("This has been the story", ['ps5cine']),
]

# music: line substring where a track starts, track, seconds skipped at its start
# (Kevin MacLeod, incompetech.com, CC BY 4.0) chosen by the catalogue's mood tags for what each section tells
MUSIC = [
 ("For most of this medium", 'Bittersweet', 0),              # somber, calm: physical games disappearing
 ("Let's get the bad news", 'Stay_the_Course', 0),           # dark, suspenseful: preservation, petitions, AI slop
 ("a leak from Insomniac", 'Half_Mystery', 0),               # mysterious, low groove: big budgets, same games
 ("Then, at The Game Awards 2025", 'Newer_Wave', 2),         # bright, uplifting: small teams win
 ("In 2019, fans finished", 'Rising_Tide', 0),               # mysterious, driving: rebuilding code
 ("But what if you didn't have to rebuild", 'Realizer', 0),  # bright, driving: ports everywhere
 ("And then, at the end of September", 'Voxel_Revolution', 0),  # bouncy, playful: Minecraft in Skyrim
 ("So where does that leave us?", 'Airship_Serenity', 0),    # calm, uplifting, slow 8-bit: closing
]
