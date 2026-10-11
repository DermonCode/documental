# Who Gets to Keep Video Games
*Guion de documental · ~8 min · narración en inglés*

## Notas de ritmo (medidas, no supuestas)
Medido sobre los subtítulos con tiempo por palabra de dos videos de Summoning Salt: *How Speedrunners Broke Spyro* (74 min) y *The Story of Mario Maker's Impossible Levels* (40 min). Excluí los sponsors y los clips de otras voces. Detalle en `investigacion.md` §8.

| Regla | Valor medido |
|---|---|
| Velocidad de narración | **158–166 palabras/min** (Spyro / Mario Maker) |
| Pausa entre oraciones | mediana **~0,9–1,0 s** (p90 ≤ 1,7 s) |
| Pausa en comas | mediana ~0,6 s |
| Largo de oración | mediana **11–12 palabras**, p90 22–25. En Spyro, el 23% tiene ≤5 palabras |
| Cortes sin voz (música o imagen sola, ≥3 s) | **0,55–0,70 por minuto**, mediana 5–8 s, máximo 22–29 s en el clímax |
| Preguntas retóricas | **2,5–5,7%** de las oraciones, solo en puntos de giro |
| Arranques de oración frecuentes | *He / But / It / This / And / So* (el "But" es el motor narrativo) |

**Patrones de estructura que se repiten en los dos videos**
- **Cold open:** primero una frase amplia ("Spyro is a game that millions…"). Después un giro con "But today, I want to take you back to…", una fecha exacta, una persona con nombre y una cita.
- **Cierre del prólogo:** una frase de título ("This is the history of how they did it.") seguida de **13–18 s solo de música**.
- **Remates cortos:** cifras sueltas como oración ("26,486.", seguida de 3,2 s de pausa), y frases como "Think about that." o "World record.".
- **Clímax:** la frase que lo anuncia ("…Sanx did this.") y después **20+ s sin voz**.
- **Cierre:** se amplía a la comunidad, termina con una pregunta abierta y "Time will tell.", y después vienen "This has been the history of…" y "Thanks for watching.".

**Convenciones de este guion:** una oración por línea. `[ ]` = imagen o sonido. `⏸ Ns` = corte sin voz de N segundos.

**Orden (v3):** primero lo malo (corto), después AAA contra indies, decompilación, recompilación estática, passthrough mods y conclusión. Más de la mitad del tiempo va a lo bueno. Misma voz y misma velocidad que v2; se recortó texto, no se aceleró.

---

## 0:00 — COLD OPEN
`[Discos y consola, b-roll moderno en 4K]`

For most of this medium's history, buying a video game meant holding something.
A cartridge. A disc. A box on a shelf that was still yours twenty years later.
That's ending.
`[Captura del post del PlayStation Blog]`
On July 1st, 2026, Sony announced that new PlayStation games would stop shipping on disc in January 2028.
And honestly?
That's not even the scary part.
Three years earlier, the Video Game History Foundation studied over 4,000 classic games released in the US before 2010.
How many could you still buy legally?
`⏸ 1,5s`
Thirteen percent.
The other 87%?
Gone.
So if the industry isn't keeping its games… who is?
This is the story of the people who decided to do it themselves.

`[TÍTULO: WHO GETS TO KEEP VIDEO GAMES — solo música]` `⏸ 12s`

---

## 0:58 — I. THE BAD NEWS
`[PS5, petición, Frank Cifaldi]`

Let's get the bad news out of the way.
Fans were furious about the discs, and one petition passed 200,000 signatures that same month.
Frank Cifaldi, who runs the Video Game History Foundation, was asked if piracy is the only real way games get preserved right now.
His answer:
"This is accurate."
`[Stop Killing Games]`
Players tried the legal route too.
Over 1.2 million Europeans signed Stop Killing Games, asking for games to stay playable after support ends.
The European Commission said a law would "not be proportionate at this stage."
`[Página de Steam bajando sin fin]`
And AI was flooding Steam with slop.
In 2024, about 11% of new releases disclosed generative AI.
By July 2026, it was 30.8%.
No discs.
No law.
Storefronts drowning.
Sounds hopeless, right?
`⏸ 1s`
It isn't.

`⏸ 3s`

---

## 1:58 — II. GIANTS AND SMALL TEAMS
`[Tráiler de Spider-Man 2]`

In 2023, a leak from Insomniac Games revealed that Marvel's Spider-Man 2 cost 315 million dollars.
When a game costs that much, nobody wants to take risks.
So you get the same game, over and over.
Over-the-shoulder camera.
Slow cinematic walks.
A map full of icons.
`[Clair Obscur gana Game of the Year]`
Then, at The Game Awards 2025, Game of the Year went to Clair Obscur: Expedition 33.
Made for under 10 million dollars, by a core team of about 30 people.
Hideo Kojima put it best.
"They only have like 33 team members and a dog."
Hollow Knight: Silksong sold over 7 million copies in three months.
Schedule I and R.E.P.O. came out of nowhere and became two of the biggest hits of 2025.
The games everyone was talking about weren't the expensive ones.
And some of the most exciting projects right now aren't even new games.
They're old games… rebuilt by fans.

`⏸ 4s`

---

## 3:00 — III. REBUILDING THE CODE
`[Super Mario 64 en PC con ray tracing]`

In 2019, fans finished something wild.
They rebuilt the entire source code of Super Mario 64.
Not emulating it.
Rewriting it, function by function, until it compiled into the exact same game.
That's called decompilation.
And once you have the code, you can take the game anywhere.
Mario 64 got a native PC port… and then ray tracing.
`[Ship of Harkinian en 4K]`
Ocarina of Time became Ship of Harkinian, in 4K, widescreen, at 120 frames per second.
Majora's Mask followed with 2 Ship 2 Harkinian.
Perfect Dark.
Star Fox 64.
Mario Kart 64.
All rebuilt, all running natively on PC.
And it's not just Nintendo.
Jak and Daxter was rebuilt through OpenGOAL, and now the whole trilogy runs on PC.
`[Repositorio de re3]`
Publishers didn't love this.
Take-Two sued the programmers behind re3, a rebuilt version of GTA III and Vice City.
But it didn't stop.
`[Melee, barra de decomp.dev al 100%]`
On September 8th, 2026, after six years of work, Super Smash Bros. Melee reached 100% decompiled.
With an asterisk.
`⏸ 1s`
"Used with AI (Claude)."
In decompilation, the compiler is the judge.
If your code is wrong, it won't match, and you know immediately.
That's exactly why AI got so good at it.
`[Snowboard Kids 2]`
One developer working on Snowboard Kids 2 put Claude in a loop.
Pick the easiest function, try to match it, give up after ten tries, move on.
He made more progress in three weeks than in the previous three months.

`⏸ 4s`

---

## 4:40 — IV. SKIPPING THE CODE
`[Código de máquina convirtiéndose en código de PC]`

But what if you didn't have to rebuild the code at all?
That's static recompilation.
Instead of rewriting a game by hand, a tool reads the original machine code and translates it straight into code a PC can run.
No emulator.
`[Majora's Mask en ultrawide]`
On May 10th, 2024, Zelda 64: Recompiled came out.
Majora's Mask, running natively on PC, in ultrawide, at high frame rates.
The tool behind it, N64: Recompiled, was open source.
So the floodgates opened.
Duke Nukem: Zero Hour.
Dr. Mario 64.
Banjo-Kazooie.
Even Dinosaur Planet, a Rare game that was cancelled and never released, now runs natively on PC.
`[Sonic Unleashed en 4K]`
Then, in March 2025, the idea jumped a generation.
Unleashed Recompiled turned the Xbox 360 version of Sonic Unleashed into a native PC port, in 4K, at 60 frames per second and beyond.
None of these include the game itself.
You bring your own copy.
They just make sure it keeps running after the hardware is gone.

`⏸ 4s`

---

## 5:52 — V. MINECRAFT IN SKYRIM
`[SkyCraft: bloques de Minecraft en Skyrim]`

And then, at the end of September 2026, things got weird.
A modder known as chasmlol released SkyCraft.
In SkyCraft, you play Skyrim… as a Minecraft player.
You break and place blocks in Skyrim's world.
You dig straight into the terrain.
You fight its NPCs with Minecraft weapons.
And here's the crazy part.
Neither game was rewritten.
Both run at the same time.
Skyrim draws everything on screen, while Minecraft runs hidden in the background, handling the player, the blocks, and the combat.
People called it a passthrough mod.
And within days, it was everywhere.
`[Un clip por cada mod]`
Minecraft in Fallout 4.
Minecraft in World of Warcraft.
Skate 3 in GTA San Andreas.
DOOM in Skyrim.
Most of them were built with AI.
You point an agent at SkyCraft's code, describe your two games, play the result, paste the errors, and repeat.
Not long ago, this took years of reverse engineering experience.
Now it takes an idea… and a lot of patience.

`⏸ 5s`

---

## 7:00 — EPILOGUE
`[Repaso de todo lo que se mostró]`

So where does that leave us?
The discs are going away, the law isn't coming, and most of gaming's past is out of print.
But Mario 64's code is out there.
Majora's Mask runs natively on PC.
Melee is fully decompiled.
And somebody put Minecraft inside Skyrim.
Not because a publisher decided to.
Because players did.
So play the games that matter to you.
Support the people preserving them.
And keep an eye on the small teams.
Most of what they make will be forgotten.
But some of it will be the next game we can't stop talking about.
And this time, hopefully, we get to keep it.
`⏸ 1s`
This has been the story of who gets to keep video games.
Thanks for watching.

`[Música final]` `⏸ 8s`

---

### Fuentes de cada afirmación
Todas las cifras, fechas y citas del guion están en `investigacion.md`, con su link. Datos que aparecen en el guion y no en el informe:
- La regla del agente en *Snowboard Kids 2* (función más fácil, 10 intentos y sigue): [Yahoo Tech](https://tech.yahoo.com/gaming/articles/pc-ports-old-console-games-160000404.html).
- La cita completa de Cifaldi: [Digital Trends](https://www.digitaltrends.com/gaming/sony-is-helping-bury-physical-games-and-preservation-is-being-left-to-clean-up-the-mess/).
- Ports y recompilaciones nombrados (Ship of Harkinian, 2 Ship 2 Harkinian, Perfect Dark, Starship, SpaghettiKart, OpenGOAL, Duke Nukem: Zero Hour, Dr. Mario 64, Banjo-Kazooie y Dinosaur Planet Recompiled): ver `fuentes.txt`.
- Passthrough mods (FalloutCraft, Minecraft en WoW, GTA San AnSkateas, SkyDoom) y la excavación de terreno en SkyCraft: ver `fuentes.txt`.
