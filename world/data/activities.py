"""
Ambient Activity Pools

Random events and observations that make spaces feel alive without
requiring actual NPCs or game systems.

These are used by rooms via the <ambient.activity> shortcode and
the activity_pool property.

Usage:
    room.activity_pool = MARKET_ACTIVITIES
    room.activity_chance = 0.3  # 30% chance to show one

Guidelines:
- Keep activities brief (one sentence)
- Include variety (sounds, sights, actions)
- Some should be atmospheric, some interactive-feeling
- Avoid activities that would require player response
- Mix mundane with occasional unusual
"""

# =============================================================================
# PLAZA ACTIVITIES
# =============================================================================

PLAZA_ACTIVITIES = [
    # People
    "A pair of travelers consult a map, looking confused.",
    "Someone rushes past, late for something important.",
    "Two old friends greet each other warmly near the fountain.",
    "A street performer sets up their instrument.",
    "A child chases a butterfly across the stones.",
    "A merchant wheels a cart toward the market.",
    "A couple sits on a bench, heads together.",
    "Someone feeds bread crumbs to the birds.",
    "A messenger runs past with urgent purpose.",
    "An elderly person rests on a bench, watching the world go by.",
    
    # Atmospheric
    "The fountain catches the light in a rainbow spray.",
    "Leaves skitter across the plaza in a sudden breeze.",
    "The bell tower chimes the hour.",
    "A flock of birds takes flight from the rooftops.",
    "Shadows shift as clouds pass overhead.",
    "The scent of baking bread drifts from somewhere nearby.",
    "Distant music floats on the breeze.",
    "A cool wind sweeps through, offering momentary relief.",
    
    # Unusual
    "For just a moment, you could swear you saw something shimmer near the gate.",
    "A wolf trots through purposefully—people step aside without concern.",
    "A raven lands on the fountain's edge, eyeing you with uncanny intelligence.",
]

# =============================================================================
# MARKET ACTIVITIES
# =============================================================================

MARKET_ACTIVITIES = [
    # Commerce
    "A merchant loudly hawks 'fresh fish, fresh fish, caught this morning!'",
    "A customer and vendor haggle fiercely over the price of fabric.",
    "Someone drops their coin purse; copper scatters everywhere.",
    "A satisfied customer walks away with a wrapped package.",
    "Two merchants argue about whose stall encroaches on whose.",
    "A vendor counts coins with practiced fingers.",
    "Someone examines a piece of pottery with a critical eye.",
    "A haggle ends with handshakes all around.",
    "A pickpocket's hand gets slapped away—'Nice try!'",
    "A regular customer gets a warm greeting and a special price.",
    
    # Atmosphere
    "The smell of spiced meat from a food stall makes your mouth water.",
    "Colorful fabrics flutter in the breeze like festival flags.",
    "A child tugs their parent toward a toy stall.",
    "The clink of coins provides a constant metallic undertone.",
    "Chalk signs advertise 'SALE TODAY' on several stalls.",
    "A vendor rearranges their display for the hundredth time.",
    
    # Unusual
    "A cloaked figure examines a stall's wares without touching anything.",
    "Something sparkles in a trinket bin—probably just glass.",
    "A cat weaves between stalls, clearly on important business.",
]

# =============================================================================
# TAVERN ACTIVITIES
# =============================================================================

TAVERN_ACTIVITIES = [
    # Patrons
    "Someone laughs too loudly at their own joke.",
    "A regular slumps in their usual corner, nursing a drink.",
    "Two strangers strike up a conversation over ale.",
    "A group erupts in cheers as someone finishes a drinking challenge.",
    "A bard tunes their instrument in the corner.",
    "Someone slams their mug down and calls for another round.",
    "A couple in the corner speaks in hushed, intense tones.",
    "A traveler studies a map, marking locations with charcoal.",
    "Someone nods off in their chair, snoring softly.",
    "A veteran tells a story that grows more elaborate with each telling.",
    
    # Atmosphere
    "The fire crackles and pops, sending sparks up the chimney.",
    "The smell of roasting meat makes your stomach growl.",
    "Pipe smoke curls toward the rafters in lazy spirals.",
    "A waitstaff deftly balances a tray of full mugs.",
    "The floorboards creak under heavy boots.",
    "Candle wax drips onto a table, unnoticed.",
    
    # Unusual
    "For a moment, the light catches someone's eyes in an odd color.",
    "The bard's song seems to have extra meaning tonight.",
    "A hooded figure in the corner hasn't touched their drink.",
]

# =============================================================================
# FOREST ACTIVITIES
# =============================================================================

FOREST_ACTIVITIES = [
    # Nature
    "A squirrel chatters angrily from a branch above.",
    "Something rustles in the underbrush—just a rabbit.",
    "A bird calls once, twice, then falls silent.",
    "Leaves drift down in a lazy spiral.",
    "A spider's web catches the light between two trees.",
    "Something small scurries across the path ahead.",
    "A deer freezes at the edge of visibility, then bounds away.",
    "The wind sighs through the branches.",
    "Mushrooms cluster at the base of an old stump.",
    "A woodpecker drums in the distance.",
    
    # Atmospheric
    "Shafts of light pierce the canopy in golden columns.",
    "The forest floor is soft and silent underfoot.",
    "Moss grows thick on the north side of every tree.",
    "The air is rich with the smell of growing things.",
    "Old trees creak and groan in the wind.",
    "Something about this place feels ancient and watchful.",
    
    # Mysterious
    "You catch a glimpse of movement, but when you look—nothing.",
    "A perfect ring of mushrooms circles a clearing. A faerie circle.",
    "The trees seem to lean in, as if listening.",
    "A path you didn't notice before beckons to the left.",
]

# =============================================================================
# WATERFRONT ACTIVITIES
# =============================================================================

WATERFRONT_ACTIVITIES = [
    # Water
    "A fish jumps, leaving ripples spreading outward.",
    "Lily pads bob gently on the water's surface.",
    "A frog croaks once, then splashes into the water.",
    "Dragonflies dance above the water's surface.",
    "The water laps gently against the shore.",
    "Something moves in the deeper water—too quick to identify.",
    "A turtle basks on a sun-warmed log.",
    "Reeds sway in the breeze, whispering secrets.",
    
    # Fishing
    "A patient fisher watches their bobber with intense focus.",
    "Someone's line goes taut—they've got something!",
    "A fisher rebaits their hook with practiced movements.",
    "An experienced angler offers unsolicited advice.",
    
    # Atmospheric
    "The smell of water and mud is somehow pleasant.",
    "Mist rises from the water's surface.",
    "The light plays strangely on the water, silver and gold.",
    "A heron stands motionless at the water's edge.",
    
    # Unusual
    "For just a moment, something beneath the surface seemed to look back at you.",
    "The water goes perfectly still, like glass, then ripples resume.",
]

# =============================================================================
# MUSEUM ACTIVITIES
# =============================================================================

MUSEUM_ACTIVITIES = [
    # Visitors
    "A visitor peers closely at a display, breath fogging the glass.",
    "Someone sketches a specimen in a leather-bound notebook.",
    "A child asks their parent 'what's THAT?' pointing excitedly.",
    "Two scholars argue quietly about classification.",
    "A visitor reads every single placard, lips moving.",
    "Someone takes a wrong turn and doubles back, embarrassed.",
    
    # Staff
    "A museum attendant straightens an already-straight placard.",
    "A curator walks through purposefully, not making eye contact.",
    "Someone with cleaning supplies polishes a display case.",
    
    # Atmosphere
    "Footsteps echo off the high ceilings.",
    "The hum of preservation magic is just barely audible.",
    "Dust motes drift in the light from skylights above.",
    "A clock somewhere ticks in the silence.",
    
    # Unsettling
    "That specimen wasn't looking at you a moment ago. Was it?",
    "A shadow moves where nothing should cast one.",
    "The Curator's gaze falls on you for just a moment—measuring.",
]

# =============================================================================
# MINE ACTIVITIES
# =============================================================================

MINE_ACTIVITIES = [
    # Work
    "The distant sound of pickaxes echoes through the tunnels.",
    "A miner pushes a cart of ore toward the surface.",
    "Someone wipes sweat from their brow, leaving a streak of dirt.",
    "A lamp flickers, then steadies.",
    "Miners share a water skin, taking turns.",
    "Someone examines a rock, then tosses it aside.",
    
    # Sounds
    "Stone settles somewhere deeper with a grinding sound.",
    "Water drips in a steady rhythm.",
    "Your footsteps echo strangely in the confined space.",
    "A distant rumble—probably just natural settling.",
    
    # Atmospheric
    "The air is thick with stone dust.",
    "Support beams creak under the weight of earth above.",
    "The darkness beyond the light seems almost solid.",
    "The temperature drops as you go deeper.",
    
    # Unusual
    "Something glitters in the wall—just mica. Probably.",
    "For a moment, you could swear you heard whispering.",
    "An old shaft is marked 'CLOSED - UNSAFE.' The boards look new.",
]

# =============================================================================
# RESIDENTIAL ACTIVITIES
# =============================================================================

RESIDENTIAL_ACTIVITIES = [
    # Daily life
    "Someone hangs laundry on a line between buildings.",
    "A dog barks, then quiets at its owner's command.",
    "A window opens and the smell of cooking drifts out.",
    "Children play a game with sticks and a ball.",
    "An elderly neighbor waves from their porch.",
    "Someone sweeps their front step, humming a tune.",
    "A cat surveys its domain from a sunny windowsill.",
    
    # Atmospheric
    "Smoke curls from chimneys, cozy and domestic.",
    "The distant sounds of a home being lived in.",
    "Garden plots show the care of their tenders.",
    "Wind chimes sing from someone's porch.",
    
    # Unusual
    "A house you don't remember sits at the end of the lane.",
    "Someone's curtain twitches—watching.",
]

# =============================================================================
# MEADOW ACTIVITIES
# =============================================================================

MEADOW_ACTIVITIES = [
    # Nature
    "A butterfly alights on a flower, wings slowly opening and closing.",
    "Bees drone from flower to flower, industrious and focused.",
    "Grasshoppers spring away from each footstep.",
    "A ladybug crawls across a blade of grass.",
    "The grass ripples in the wind like a green sea.",
    "A meadowlark sings from somewhere in the golden waves.",
    
    # Atmospheric
    "The sun is warm on your face and shoulders.",
    "The smell of wildflowers is almost intoxicating.",
    "Seeds drift on the breeze like tiny parachutes.",
    "A rabbit watches you from the grass, nose twitching.",
    
    # Unusual
    "A patch of flowers seems to sway differently than the wind dictates.",
    "You spot something in the grass—just an old bottle, probably lost.",
]

# =============================================================================
# QUARRY ACTIVITIES
# =============================================================================

QUARRY_ACTIVITIES = [
    # Work
    "The crack of chisel on stone rings out.",
    "Someone hoists a block of stone onto a cart.",
    "A stone cutter examines a fresh break, nodding in satisfaction.",
    "Dust billows from a recent cut.",
    
    # Atmospheric
    "The walls of the quarry tower above, showing layers of stone.",
    "Heat radiates from sun-warmed rock.",
    "The acoustics make sounds carry strangely.",
    "Stone dust covers everything in a pale coating.",
    
    # Unusual
    "A fossil emerges from the rock—something ancient.",
    "The stone seems to change color as the light shifts.",
]

# =============================================================================
# TIME-SPECIFIC ACTIVITIES
# =============================================================================

DAWN_ACTIVITIES = [
    "The first birds begin their morning chorus.",
    "Dew glitters on every surface.",
    "Someone yawns, not quite awake yet.",
    "Shutters open as the day begins.",
    "The smell of breakfast cooking drifts on the air.",
]

MORNING_ACTIVITIES = [
    "The day is still full of possibility.",
    "People move with morning energy.",
    "The light has that fresh, golden quality.",
    "Coffee (or its equivalent) is being consumed in quantity.",
]

EVENING_ACTIVITIES = [
    "Shadows stretch long across the ground.",
    "People head home after a day's work.",
    "Lamps and candles begin to glow in windows.",
    "The light takes on a warm, golden quality.",
    "Birds return to roosts, singing last songs.",
]

NIGHT_ACTIVITIES = [
    "Stars wheel overhead in silent majesty.",
    "The sounds of the day have faded to night sounds.",
    "Most windows are dark; the honest folk abed.",
    "Your footsteps seem louder in the quiet.",
    "The moon casts silver light and black shadows.",
]

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PLAZA_ACTIVITIES",
    "MARKET_ACTIVITIES",
    "TAVERN_ACTIVITIES",
    "FOREST_ACTIVITIES",
    "WATERFRONT_ACTIVITIES",
    "MUSEUM_ACTIVITIES",
    "MINE_ACTIVITIES",
    "RESIDENTIAL_ACTIVITIES",
    "MEADOW_ACTIVITIES",
    "QUARRY_ACTIVITIES",
    "DAWN_ACTIVITIES",
    "MORNING_ACTIVITIES",
    "EVENING_ACTIVITIES",
    "NIGHT_ACTIVITIES",
]
