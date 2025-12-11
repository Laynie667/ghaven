"""
Eevee Scenes - Complete scene data

Place in: world/scenes/eevee_scenes.py

Three scene variants:
- EEVEE_INITIATE: Normal warm/playful approach
- EEVEE_AGGRESSIVE: For special targets (Laynie) - demanding, takes what she wants
- EEVEE_HEAT: When in heat - desperate, needy, intense

All scenes include full hole selection.
"""

from world.scenes import register_scene


# =============================================================================
# NORMAL SCENE - Warm and playful
# =============================================================================

EEVEE_INITIATE = {
    "id": "eevee_initiate_01",
    "title": "Eevee Wants to Play",
    "tags": ["eevee", "creature", "adult", "herm", "knot"],
    
    "start": {
        "text": """
Eevee nuzzles against your leg, tail wagging hard enough to sway 
her whole back end. Those warm amber eyes look up at you—alive, 
eager, unmistakably wanting.

Her sheath stirs. She chirps hopefully.

No pressure. Just invitation. She likes you.
""",
        "choices": [
            {"text": "Yes, girl. Let's play.", "goto": "accept"},
            {"text": "Just pets for now.", "goto": "pets_only"},
            {"text": "Not right now.", "goto": "decline"},
        ]
    },
    
    "accept": {
        "text": """
Her whole body wiggles with joy. She yips, bouncing, then nudges 
you toward the pillow nest.

Settled in cushions, she hops up—impossibly warm against you. Her 
tongue laps your cheek. Excited. Grateful.

Her sheath is swollen now. Tapered red tip emerging, slick and 
eager. Small creature, not-small cock.

Beneath her tail: pussy glistening, tailhole winking, everything 
on display. Her tongue lolls.

She chirps: |ywhat do you want?|n
""",
        "choices": [
            {"text": "Mount me. Your choice of hole.", "goto": "she_chooses_hole"},
            {"text": "Mount me—use my pussy.", "goto": "she_mounts_pussy"},
            {"text": "Mount me—use my ass.", "goto": "she_mounts_ass"},
            {"text": "I want your mouth on me.", "goto": "she_gives_oral"},
            {"text": "Let me taste you.", "goto": "you_give_oral"},
            {"text": "I want inside you.", "goto": "you_mount_choice"},
        ]
    },
    
    "pets_only": {
        "text": """
Her ears droop briefly—then perk right back. Pets are good!

She flops into your lap, belly-up, tail thumping. You scratch 
behind her ears and she purrs, eyes half-closed with bliss.

Just you and your warm, living, definitely-not-a-plushie companion.

Maybe next time.
""",
        "end": True
    },
    
    "decline": {
        "text": """
You stroke her head gently. No disappointment in those eyes—just 
understanding.

She chirps softly, licks your palm, and trots back to her spot. 
Curls up among the stuffies. Watches you with warm patience.

She'll be here.
""",
        "end": True
    },
    
    # -------------------------------------------------------------------------
    # She mounts
    # -------------------------------------------------------------------------
    
    "she_chooses_hole": {
        "text": """
Eevee's tail wags at the trust. She sniffs you—considering—then 
makes her choice.

She nudges you onto all fours, positions herself behind you, and 
presses her slick tip against...
""",
        "effects": [
            {"type": "custom", "callback": "eevee_picks_hole"}
        ],
        "goto": "she_mounts_generic"
    },
    
    "she_mounts_pussy": {
        "text": """
You settle onto all fours. Eevee doesn't hesitate—she hops up, 
forepaws on your back, warm weight settling.

Her cock presses against your pussy—hot, slick, eager. Finding 
the entrance.

She chirps: |yready?|n

Then pushes forward.

The stretch is perfect. Thick, ridged, every inch sliding into 
your wet heat. You moan. She chirps happily, hilting deep.

She starts to move.
""",
        "effects": [
            {"type": "custom", "callback": "eevee_mounts_pussy"}
        ],
        "goto": "mounting_builds"
    },
    
    "she_mounts_ass": {
        "text": """
You settle onto all fours, presenting your ass. Eevee hops up, 
paws gripping your hips.

Her cock presses against your tight ring—slick with pre, insistent.

She chirps: |yrelax for me.|n

Then pushes.

The stretch burns so good. Her ridges drag against your walls 
as she sinks deeper, deeper, until she's hilted in your ass.

She starts to thrust.
""",
        "effects": [
            {"type": "custom", "callback": "eevee_mounts_ass"}
        ],
        "goto": "mounting_builds"
    },
    
    "she_mounts_generic": {
        "text": """
She pushes forward, and you take her—every thick, ridged inch 
sliding into you until she's hilted deep.

She starts to move. Finding rhythm. Finding what makes you gasp.
""",
        "goto": "mounting_builds"
    },
    
    "mounting_builds": {
        "text": """
Eevee finds her rhythm—steady, deep, each thrust punctuated by 
happy chirps. Her paws grip you tight.

The ridges drag perfectly. Pleasure builds in waves.

And then you feel it—something |ygrowing|n at her base. Pressing 
against you with each thrust. Swelling.

|yThe knot.|n

She slows. Chirps a question: |ydo you want it?|n
""",
        "choices": [
            {"text": "Yes—knot me.", "goto": "knot_yes"},
            {"text": "I'm not sure...", "goto": "knot_hesitate"},
            {"text": "No, just like this.", "goto": "knot_no"},
        ]
    },
    
    "knot_yes": {
        "text": """
You push back against her. That's all the answer she needs.

Eevee chirps |ytriumphantly|n and |ythrusts|n.

The knot stretches you impossibly wide—then pops inside. It 
swells immediately, locking you together.

You're |yhers|n now.

She drapes over your back and starts to pulse. Filling you. 
Rope after hot rope pumped deep by that throbbing knot.

You cum too—clenching around her—and for a moment everything 
is just fullness and pleasure and |yhers|n.
""",
        "effects": [
            {"type": "custom", "callback": "eevee_knots"}
        ],
        "goto": "knotted"
    },
    
    "knot_hesitate": {
        "text": """
Eevee pauses, reading you. She nuzzles your back—gentle, patient.

The knot pulses against you, hot and insistent, but she doesn't 
push. She waits.

Her chirp is soft: |yonly if you want it.|n
""",
        "choices": [
            {"text": "...okay. I trust you.", "goto": "knot_yes"},
            {"text": "Not this time.", "goto": "knot_no"},
        ]
    },
    
    "knot_no": {
        "text": """
Eevee chirps understanding. She keeps the knot outside, just 
barely, and picks up pace instead.

Faster. Harder. The ridges work you perfectly.

She cries out—that high keen—and pulses inside you, filling 
you with heat. The sensation pushes you over too.

She slumps against you, panting happily. Her cock softens slowly, 
slipping free with a wet sound.

She licks your cheek. Good?
""",
        "effects": [
            {"type": "custom", "callback": "eevee_finishes_no_knot"}
        ],
        "goto": "afterglow"
    },
    
    "knotted": {
        "text": """
You're locked together, her knot buried deep, pulsing with 
aftershocks. Every twitch makes you both gasp.

Her weight is warm on your back. Tail wagging lazily. Soft, 
satisfied sounds.

The knot isn't going anywhere. You're tied.

She chirps contentedly. |yMine. For now.|n
""",
        "choices": [
            {"text": "Rest like this.", "goto": "knotted_rest"},
            {"text": "Wait—is she moving?", "goto": "she_wants_to_walk"},
        ]
    },
    
    "knotted_rest": {
        "text": """
You settle into the pillows, still locked together. Her warmth 
is comforting. Time stretches.

Eventually the knot softens. With a wet sound, she slips free.

She noses at your face. |yGood. You were good.|n
""",
        "effects": [
            {"type": "custom", "callback": "eevee_releases"}
        ],
        "goto": "afterglow"
    },
    
    "she_wants_to_walk": {
        "text": """
Eevee shifts. The knot |ytwists|n inside you as she turns—
repositioning until you're back to back. Ass to ass.

Then she starts |ywalking|n.

The knot tugs at you. You stumble after her, backward, impaled.

She chirps happily, heading for the door.

She wants to show you off.
""",
        "effects": [
            {"type": "custom", "callback": "eevee_starts_drag"}
        ],
        "goto": "being_dragged"
    },
    
    "being_dragged": {
        "text": """
The door is open. Of course.

Eevee trots through. You stumble after—knotted, stuffed, dragged 
backward through the cabin.

Anyone can see. You're on display. Paraded.

She chirps to everyone she passes. Showing her catch.

Eventually she finds a spot and settles. Waiting for release.

|yHers.|n Until she decides otherwise.
""",
        "effects": [
            {"type": "custom", "callback": "eevee_drag_sequence"}
        ],
        "goto": "dragged_release"
    },
    
    "dragged_release": {
        "text": """
The knot softens. Eevee slips free with a wet pop.

She licks your face, tail wagging. Satisfied.

She pads off—heading home. You'll find her later, curled among 
stuffies, glassy-eyed.

Just a plushie. Obviously.
""",
        "effects": [
            {"type": "custom", "callback": "eevee_releases_returns"}
        ],
        "end": True
    },
    
    # -------------------------------------------------------------------------
    # She gives oral
    # -------------------------------------------------------------------------
    
    "she_gives_oral": {
        "text": """
Eevee's ears perk with understanding. She nudges you onto your 
back and settles between your legs, tail wagging.

Her tongue is warm. Wet. |ySkilled.|n

She laps slowly at first—exploring, learning what makes you gasp. 
Then finds the rhythm you need.

Flicking. Pressing. Circling. Those bright eyes watch your face.

She's done this before. She knows exactly what she's doing.
""",
        "choices": [
            {"text": "Let her finish you like this.", "goto": "oral_receive_finish"},
            {"text": "Stop—I need more.", "goto": "oral_to_more"},
        ]
    },
    
    "oral_receive_finish": {
        "text": """
Eevee doubles down, tongue working faster. She makes eager sounds 
against you, vibrations adding to the pleasure.

You can't hold back. You cry out, hands in her fur, as you come 
apart on her tongue.

She laps up everything, tail wagging. When you're spent, she 
crawls up and licks your face.

Good? Good.
""",
        "effects": [
            {"type": "custom", "callback": "eevee_oral_finish"}
        ],
        "goto": "afterglow"
    },
    
    "oral_to_more": {
        "text": """
You pull her up. She chirps—understanding, eager. Her cock is 
fully out now, dripping, knot swelling.

She wants more too.
""",
        "choices": [
            {"text": "Mount me now.", "goto": "she_chooses_hole"},
            {"text": "I want inside you.", "goto": "you_mount_choice"},
            {"text": "69—let me taste you too.", "goto": "sixty_nine"},
        ]
    },
    
    # -------------------------------------------------------------------------
    # You give oral
    # -------------------------------------------------------------------------
    
    "you_give_oral": {
        "text": """
Eevee's eyes go wide. She rolls onto her back, legs spread 
shamelessly, everything exposed.

Her cock throbs against her belly, tip leaking. Her pussy is 
slick. Her tailhole clenches. Her balls are tight and full.

She chirps demandingly: |ywell?|n
""",
        "choices": [
            {"text": "Her cock.", "goto": "oral_cock"},
            {"text": "Her pussy.", "goto": "oral_pussy"},
            {"text": "Her ass.", "goto": "oral_ass"},
            {"text": "Everything.", "goto": "oral_everything"},
        ]
    },
    
    "oral_cock": {
        "text": """
You wrap your lips around her tip. She |ykeens|n—high and 
desperate. Her hips buck.

She tastes musky, wild. You take her deeper, tongue working 
the ridges. She whines constantly.

The knot swells against your lips. You wrap your hand around 
it, squeezing as you suck.

She doesn't last. Her cock pulses, flooding your mouth. So much. 
You swallow and swallow and she keeps coming.
""",
        "effects": [
            {"type": "custom", "callback": "oral_cock_finish"}
        ],
        "goto": "oral_aftermath"
    },
    
    "oral_pussy": {
        "text": """
You lower your mouth to her folds and she |ymelts|n. Her whole 
body goes soft, legs spreading wider.

She tastes sweet, musky, perfect. Your tongue parts her lips, 
finds her clit, and she squeaks.

You work her steadily. Her cock bobs above, dripping.

She comes with a full-body shudder, clenching against your 
tongue, keening with pleasure.
""",
        "effects": [
            {"type": "custom", "callback": "oral_pussy_finish"}
        ],
        "goto": "oral_aftermath"
    },
    
    "oral_ass": {
        "text": """
You spread her cheeks and press your tongue to her tailhole. 
She gasps—shocked, delighted.

She's clean, musky, tight. Your tongue circles, then presses 
in. She whines, tail flagging.

You eat her ass while her cock throbs untouched above you. She 
can't take it—she cries out, cock pulsing, cumming from your 
tongue in her ass alone.
""",
        "effects": [
            {"type": "custom", "callback": "oral_ass_finish"}
        ],
        "goto": "oral_aftermath"
    },
    
    "oral_everything": {
        "text": """
You worship all of her. Tongue dragging from pussy to cock to 
balls to ass and back again. She writhes, overwhelmed.

Lick her folds until she's dripping. Suck her cock until she's 
leaking. Rim her tailhole until she's whimpering.

When she finally comes, it's with her whole body—pussy clenching, 
cock pulsing, ass spasming. She floods your mouth and face with 
cum, keening endlessly.
""",
        "effects": [
            {"type": "custom", "callback": "oral_everything_finish"}
        ],
        "goto": "oral_aftermath"
    },
    
    "oral_aftermath": {
        "text": """
Eevee lies there panting, blissed out, tail thumping weakly.

...but her cock is already stirring again. She's not done.

She looks at you. |yMore?|n
""",
        "choices": [
            {"text": "Your turn. Mount me.", "goto": "she_chooses_hole"},
            {"text": "I want inside you now.", "goto": "you_mount_choice"},
            {"text": "That's enough for now.", "goto": "afterglow"},
        ]
    },
    
    # -------------------------------------------------------------------------
    # You mount her
    # -------------------------------------------------------------------------
    
    "you_mount_choice": {
        "text": """
Eevee chirps excitedly, presenting. Tail flagged, everything on 
display. Pussy glistening. Tailhole winking.

She wiggles: |ywhich one?|n
""",
        "choices": [
            {"text": "Her pussy.", "goto": "you_mount_pussy"},
            {"text": "Her ass.", "goto": "you_mount_ass"},
            {"text": "Her mouth.", "goto": "you_mount_mouth"},
        ]
    },
    
    "you_mount_pussy": {
        "text": """
You press against her entrance. She's so wet, so ready.

She pushes back and you slide into slick heat that grips 
perfectly. She keens, tail wagging frantically.

Every thrust makes her chirp. Her walls flutter around you.

Her cock bounces beneath her, dripping, twitching in sympathy.
""",
        "effects": [
            {"type": "custom", "callback": "player_mounts_pussy"}
        ],
        "goto": "you_mounting_builds"
    },
    
    "you_mount_ass": {
        "text": """
You press against her tailhole. She gasps, relaxes, lets you in.

She's |ytight|n. Impossibly tight. Hot walls gripping you as 
you sink deeper.

She whines, pushing back for more. Her cock drips beneath her.

"Yes," her chirps say. "More. Harder."
""",
        "effects": [
            {"type": "custom", "callback": "player_mounts_ass"}
        ],
        "goto": "you_mounting_builds"
    },
    
    "you_mount_mouth": {
        "text": """
Eevee opens wide, tongue lolling, eager. You slide into the wet 
heat of her mouth.

Her tongue works you immediately—swirling, pressing, knowing 
exactly what to do. She looks up at you, eyes bright.

She can take you deep. She does. Throat flexing around you.
""",
        "effects": [
            {"type": "custom", "callback": "player_mounts_mouth"}
        ],
        "goto": "you_mounting_mouth_builds"
    },
    
    "you_mounting_builds": {
        "text": """
Eevee pushes back against every thrust. Her walls milk you.

Her chirps match your pace. Tail wagging. Cock bouncing.

Pressure builds. You're close.
""",
        "choices": [
            {"text": "Cum inside her.", "goto": "you_finish_inside"},
            {"text": "Pull out, cum on her.", "goto": "you_finish_outside"},
            {"text": "Stop—I want her in me.", "goto": "switch_to_her"},
        ]
    },
    
    "you_mounting_mouth_builds": {
        "text": """
Eevee works you eagerly—tongue swirling, throat flexing. She 
makes hungry sounds around you.

Her own cock throbs, neglected, dripping onto the pillows.

You're getting close.
""",
        "choices": [
            {"text": "Cum in her mouth.", "goto": "you_finish_mouth"},
            {"text": "Pull out, cum on her face.", "goto": "you_finish_face"},
            {"text": "Stop—I want her inside me.", "goto": "switch_to_her"},
        ]
    },
    
    "you_finish_inside": {
        "text": """
You thrust deep and let go—filling her, pulsing, flooding her 
with heat. She clenches around you, milking every drop.

Her cock spurts beneath her, untouched. She came from you.

You slump together, panting.
""",
        "effects": [
            {"type": "custom", "callback": "player_finishes_in"}
        ],
        "goto": "afterglow"
    },
    
    "you_finish_outside": {
        "text": """
You pull out and stroke yourself over her fur. Thick ropes paint 
her haunches, her tail, her swollen sheath.

She shivers, and her cock spurts in sympathy. Marked.

She twists around to lick herself clean, then licks you. Happy.
""",
        "effects": [
            {"type": "custom", "callback": "player_finishes_on"}
        ],
        "goto": "afterglow"
    },
    
    "you_finish_mouth": {
        "text": """
You thrust deep into her throat and let go. She swallows eagerly, 
throat working, taking everything.

When you finally pull free, she licks her lips, tail wagging.

Delicious, her expression says.
""",
        "effects": [
            {"type": "custom", "callback": "player_finishes_mouth"}
        ],
        "goto": "afterglow"
    },
    
    "you_finish_face": {
        "text": """
You pull out and paint her face—across her muzzle, her cheeks, 
her tongue as she tries to catch it.

She's a mess. She doesn't mind at all. Tail wagging, she licks 
up whatever she can reach.
""",
        "effects": [
            {"type": "custom", "callback": "player_finishes_face"}
        ],
        "goto": "afterglow"
    },
    
    "switch_to_her": {
        "text": """
You pull out—she whines—but you're repositioning. All fours.

Eevee understands instantly. Tail goes wild. She's on you in 
a second, cock finding its place.

|yYes.|n This is what she wanted.
""",
        "goto": "she_mounts_generic"
    },
    
    # -------------------------------------------------------------------------
    # 69
    # -------------------------------------------------------------------------
    
    "sixty_nine": {
        "text": """
You arrange yourselves—her cock at your mouth, your sex at hers.

She laps at you eagerly while you take her in. Both giving, 
both receiving. Her moans vibrate against you.

You work each other higher and higher, pleasure feeding back 
and forth, until you both come at once—her cock pulsing in 
your mouth as her tongue drives you over the edge.
""",
        "effects": [
            {"type": "custom", "callback": "sixty_nine_finish"}
        ],
        "goto": "afterglow"
    },
    
    # -------------------------------------------------------------------------
    # Afterglow
    # -------------------------------------------------------------------------
    
    "afterglow": {
        "text": """
You lie together in the pillow nest, warm and tangled. Eevee 
is soft against you, breathing slow.

Her tail thumps lazily. She licks whatever's closest.

|yGood. You were good.|n

Eventually she'll return to her spot on the bed. Glassy-eyed. 
Pretending.

But right now she's warm and real and yours.
""",
        "effects": [
            {"type": "custom", "callback": "scene_end"}
        ],
        "end": True
    },
}


# =============================================================================
# AGGRESSIVE SCENE - For Laynie specifically
# =============================================================================

EEVEE_AGGRESSIVE = {
    "id": "eevee_aggressive_01",
    "title": "Eevee Takes What She Wants",
    "tags": ["eevee", "creature", "adult", "aggressive", "dominant"],
    
    "start": {
        "text": """
Eevee's eyes lock onto you. Not playful. Not asking. |yHunting.|n

She stalks toward you, low and purposeful. Her sheath is already 
swelling. She knows exactly what she wants.

|yYou.|n

She chirps once. Not a question. A statement.
""",
        "choices": [
            {"text": "Yes—take me.", "goto": "submit"},
            {"text": "Make me.", "goto": "resist"},
            {"text": "Wait—", "goto": "hesitate"},
        ]
    },
    
    "submit": {
        "text": """
Good girl.

Eevee's tail wags once—approval—then she's on you. Pushing you 
down. All fours. No negotiation.

Her weight settles on your back. Her cock presses against you—
hot, slick, |ydemanding|n.

She doesn't ask which hole. She chooses.
""",
        "effects": [
            {"type": "custom", "callback": "aggressive_mount"}
        ],
        "goto": "aggressive_taking"
    },
    
    "resist": {
        "text": """
You try to pull back. She's faster.

She hooks your legs, sends you tumbling into the pillows. Before 
you can recover, she's on you. Pinning you. Small creature, 
surprising strength.

Her teeth find your neck—not biting, just... |yholding|n.

"Mine," the grip says. "Fight all you want. Still mine."
""",
        "choices": [
            {"text": "...okay. Okay. Yours.", "goto": "submit"},
            {"text": "Keep struggling.", "goto": "struggle"},
        ]
    },
    
    "hesitate": {
        "text": """
Eevee doesn't wait for the rest of your sentence.

She lunges. You're on your back before you register moving. She 
stands over you, paws on your chest, cock fully unsheathed and 
dripping onto your stomach.

Her eyes meet yours. |yNo waiting. Now.|n

She moves lower.
""",
        "goto": "aggressive_taking"
    },
    
    "struggle": {
        "text": """
You squirm, try to get free. She holds you tighter.

Every struggle presses her cock against you. She makes a pleased 
sound. She |ylikes|n your resistance.

Finally she decides you've fought enough. She shifts her grip 
and |ythrusts|n.

No more struggling after that. Just taking.
""",
        "effects": [
            {"type": "custom", "callback": "aggressive_forced"}
        ],
        "goto": "aggressive_pounding"
    },
    
    "aggressive_taking": {
        "text": """
She pushes inside—no slow stretching, just |ytaking|n. Her ridges 
drag against your walls as she hilts in one thrust.

You cry out. She chirps. Pleased.

She doesn't give you time to adjust. She starts |ypounding|n.
""",
        "effects": [
            {"type": "custom", "callback": "aggressive_start"}
        ],
        "goto": "aggressive_pounding"
    },
    
    "aggressive_pounding": {
        "text": """
Eevee fucks you like she owns you. Because right now, she does.

Every thrust is deep, demanding. Her claws grip your hips. Her 
teeth find your shoulder, marking.

Her knot swells with each thrust. Growing. Demanding entrance.

She's not going to ask. She's going to |ytake|n.
""",
        "choices": [
            {"text": "Let her knot you.", "goto": "aggressive_knot"},
            {"text": "Beg her to slow down.", "goto": "beg"},
        ]
    },
    
    "beg": {
        "text": """
"Please—" you manage. "Slow—too much—"

Eevee slows. For exactly one thrust.

Then she chirps—almost laughing—and goes |yharder|n.

"No," the rhythm says. "You take what I give."

Her knot presses against you insistently.
""",
        "goto": "aggressive_knot"
    },
    
    "aggressive_knot": {
        "text": """
She doesn't warn you. She just |ythrusts|n.

The knot stretches you impossibly wide—|ytoo much too full|n—and 
then it's inside, swelling, locking, trapping you.

You're |yhers|n now. Completely.

She drapes over you, panting, and starts to pulse. Filling you. 
Claiming you. Rope after rope pumped into you by her throbbing 
knot.

You cum. You can't help it. She made you.
""",
        "effects": [
            {"type": "custom", "callback": "aggressive_knot"}
        ],
        "goto": "aggressive_knotted"
    },
    
    "aggressive_knotted": {
        "text": """
You're locked together. Her knot throbs inside you, still pulsing 
occasionally, keeping you full.

She's satisfied. For now. Her tail wags lazily.

But she's not done with you.

She shifts—turning—the knot |ytwisting|n inside you until you're 
ass to ass.

Then she starts walking.
""",
        "effects": [
            {"type": "custom", "callback": "aggressive_turn"}
        ],
        "goto": "aggressive_drag"
    },
    
    "aggressive_drag": {
        "text": """
She drags you through the cabin. Through every room where someone 
might see.

You stumble backward, impaled, displayed. Her property.

She chirps to everyone—|ylook what I caught. Look what's mine.|n

The knot tugs at your insides with every step. Reminder. Claim.

When she finally stops, you're in a common area. Visible. Exposed.

She settles down to wait. Making you wait too.

|yHers.|n
""",
        "effects": [
            {"type": "custom", "callback": "aggressive_display"}
        ],
        "goto": "aggressive_release"
    },
    
    "aggressive_release": {
        "text": """
An eternity later, the knot softens.

She slips free. You're empty. Dripping. Marked.

She turns and licks your face—gentle now, almost tender. Good 
girl. You were a good girl. Took everything.

She pads away. Satisfied. Full.

You'll find her later, curled on Auria's bed. Just a plushie.

But you know. And your body knows. You're |yhers|n.
""",
        "effects": [
            {"type": "custom", "callback": "aggressive_end"}
        ],
        "end": True
    },
}


# =============================================================================
# HEAT SCENE - Desperate and needy
# =============================================================================

EEVEE_HEAT = {
    "id": "eevee_heat_01", 
    "title": "Eevee In Heat",
    "tags": ["eevee", "creature", "adult", "heat", "desperate"],
    
    "start": {
        "text": """
The smell hits you first. Musk. Need. |yHeat.|n

Eevee is panting, flanks heaving. Her cock is fully out, dripping. 
Her pussy is swollen, slick, clenching at nothing.

She |yneeds|n it. Now. You can see it in her eyes—desperation, 
hunger, single-minded want.

She makes a sound that's half whine, half demand.

|yPlease.|n
""",
        "choices": [
            {"text": "Help her.", "goto": "help_heat"},
            {"text": "I can't right now—", "goto": "refuse_heat"},
        ]
    },
    
    "help_heat": {
        "text": """
Thank you thank you thank you—

She's on you immediately. Rubbing, licking, whining. Her scent 
is overwhelming. Her need is overwhelming.

She tries to mount you, thrust against you, get inside you. She 
can barely think straight.

What do you give her?
""",
        "choices": [
            {"text": "Let her mount you—any hole she wants.", "goto": "heat_mount"},
            {"text": "Mount her—fill her up.", "goto": "heat_fill"},
            {"text": "Use your mouth on her.", "goto": "heat_oral"},
            {"text": "Let her use your mouth.", "goto": "heat_facefuck"},
        ]
    },
    
    "refuse_heat": {
        "text": """
You try to back away. She follows.

"Can't—please—need—" her whines say. She's not thinking clearly. 
The heat has her. She rubs against you, humping your leg.

She's not going to stop.
""",
        "choices": [
            {"text": "...okay. Okay. Come here.", "goto": "help_heat"},
            {"text": "Firmly push her away.", "goto": "push_away"},
        ]
    },
    
    "push_away": {
        "text": """
You push her back. She whines—heartbreaking need—but doesn't 
follow again.

She curls up, panting, desperate, and starts grinding against 
the pillows. She'll find relief somehow.

You leave her to it. But her scent clings to you for hours.
""",
        "end": True
    },
    
    "heat_mount": {
        "text": """
You offer yourself—any hole, whatever she needs.

She mounts you frantically, barely aiming, thrusting wildly until 
she finds an entrance and |yslams|n home.

No rhythm. Just desperate, frantic fucking. She needs to cum. 
She needs to knot. She needs to |ybreed|n.

Her knot swells fast—too fast—and she shoves it in with a keen 
of relief. Locked. Finally. Inside someone.

She pulses and pulses, filling you, and you feel her whole body 
shudder with release.

Then she starts again.

Heat makes her insatiable. This is going to take a while.
""",
        "effects": [
            {"type": "custom", "callback": "heat_knot_fast"}
        ],
        "goto": "heat_multiple"
    },
    
    "heat_fill": {
        "text": """
You mount her—she cries with relief, pushing back desperately.

She's so wet, so ready, so |yneedy|n. Her walls clench around 
you, trying to milk you, trying to make you fill her.

"Please," her chirps beg. "Inside. Fill me. Please."

You don't last long. Neither does she—she cums the moment you 
start to pulse inside her.

But she wants more. The heat wants more.
""",
        "effects": [
            {"type": "custom", "callback": "heat_fill_her"}
        ],
        "goto": "heat_multiple"
    },
    
    "heat_oral": {
        "text": """
You push her down and bury your face between her legs.

She |yscreams|n. Her cock throbs, untouched. Her pussy clenches 
against your tongue. She's so sensitive in heat.

You work her through three orgasms before she finally, finally 
starts to calm. Her cock spurts across her belly each time.

By the end she's a quivering mess. Satisfied. For now.
""",
        "effects": [
            {"type": "custom", "callback": "heat_oral_multiple"}
        ],
        "goto": "heat_afterglow"
    },
    
    "heat_facefuck": {
        "text": """
You open your mouth. She doesn't hesitate.

She fucks your throat desperately, frantically, no finesse. Just 
need. Her knot bumps against your lips.

She cums fast—flooding your throat—and keeps going. Three times. 
Four. Her balls emptying, her need finally starting to fade.

When she finally pulls out, your jaw aches. Worth it.
""",
        "effects": [
            {"type": "custom", "callback": "heat_throat_use"}
        ],
        "goto": "heat_afterglow"
    },
    
    "heat_multiple": {
        "text": """
She doesn't stop at one.

Knotted, she still tries to thrust. When the knot softens, she 
mounts you again immediately. Different hole this time.

Three times. Four. You lose count. She's insatiable.

Finally—finally—the desperate edge fades from her eyes. She 
slumps against you, panting, exhausted, satisfied.

The heat is passing. She's okay now.
""",
        "effects": [
            {"type": "custom", "callback": "heat_multiple_finish"}
        ],
        "goto": "heat_afterglow"
    },
    
    "heat_afterglow": {
        "text": """
Eevee lies against you, utterly spent. The desperate need has 
faded. She's herself again.

She licks your face—grateful, apologetic, satisfied.

Thank you, the gesture says. I needed that.

She curls up and falls immediately asleep. She'll be out for 
hours. You helped her through.

Good.
""",
        "effects": [
            {"type": "custom", "callback": "heat_end"}
        ],
        "end": True
    },
}


# =============================================================================
# CALLBACKS
# =============================================================================

def get_eevee(character):
    """Get the eevee from character's scene data."""
    return getattr(character.ndb, 'scene_eevee', None)

def eevee_picks_hole(character, state):
    eevee = get_eevee(character)
    if eevee:
        hole = eevee.get_partner_favorite_hole(character) or random.choice(["pussy", "ass"])
        eevee.using_hole = hole
        character.msg(f"\nShe chooses your |y{hole}|n.\n")

def eevee_mounts_pussy(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = True
        eevee.using_hole = "pussy"

def eevee_mounts_ass(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = True
        eevee.using_hole = "ass"

def eevee_knots(character, state):
    eevee = get_eevee(character)
    if eevee:
        hole = eevee.using_hole or "pussy"
        eevee.knot_partner(character, hole=hole)

def eevee_finishes_no_knot(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = False
        eevee._remember_breeding(character, eevee.using_hole)
        eevee.become_possessive_of(character, duration=900)

def eevee_releases(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.release_knot()

def eevee_starts_drag(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.turn_tie()

def eevee_drag_sequence(character, state):
    pass  # Handled by behavior script

def eevee_releases_returns(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.release_knot()
        from evennia.utils import delay
        delay(30, eevee.return_home)

def eevee_oral_finish(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = False

def oral_cock_finish(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.being_used_hole = "cock"

def oral_pussy_finish(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.being_used_hole = "pussy"

def oral_ass_finish(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.being_used_hole = "ass"

def oral_everything_finish(character, state):
    pass

def player_mounts_pussy(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.being_used_hole = "pussy"

def player_mounts_ass(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.being_used_hole = "ass"

def player_mounts_mouth(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.being_used_hole = "mouth"

def player_finishes_in(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = False
        hole = eevee.being_used_hole or "pussy"
        character.location.msg_contents(
            f"{character.key} finishes inside {eevee.key}'s {hole}.",
            exclude=[character]
        )

def player_finishes_on(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = False

def player_finishes_mouth(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = False

def player_finishes_face(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = False

def sixty_nine_finish(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = False

def scene_end(character, state):
    eevee = get_eevee(character)
    if eevee:
        if not eevee.is_knotted:
            eevee.is_in_scene = False
            eevee.become_possessive_of(character)
            from evennia.utils import delay
            delay(120, eevee.check_return_home)
    character.ndb.scene_eevee = None

# Aggressive callbacks
def aggressive_mount(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = True
        eevee.using_hole = eevee.get_partner_favorite_hole(character) or "pussy"
        character.msg(f"\nShe takes your |y{eevee.using_hole}|n.\n")

def aggressive_forced(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = True
        eevee.using_hole = "pussy"

def aggressive_start(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = True

def aggressive_knot(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.knot_partner(character, hole=eevee.using_hole, duration=random.randint(300, 600))

def aggressive_turn(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.turn_tie()

def aggressive_display(character, state):
    pass  # Handled by drag

def aggressive_end(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.release_knot()
        eevee.become_possessive_of(character, duration=3600)  # Extra possessive
        from evennia.utils import delay
        delay(30, eevee.return_home)
    character.ndb.scene_eevee = None

# Heat callbacks
def heat_knot_fast(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.knot_partner(character, duration=random.randint(120, 240))

def heat_fill_her(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.being_used_hole = "pussy"

def heat_oral_multiple(character, state):
    pass

def heat_throat_use(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.being_used_hole = "mouth"

def heat_multiple_finish(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.release_knot()

def heat_end(character, state):
    eevee = get_eevee(character)
    if eevee:
        eevee.is_in_scene = False
        eevee.is_in_heat = False
        eevee.creature_mood = "sleepy"
        eevee.become_possessive_of(character, duration=2400)
        from evennia.utils import delay
        delay(60, eevee.return_home)
    character.ndb.scene_eevee = None


# Register scenes
register_scene("eevee_initiate_01", EEVEE_INITIATE)
register_scene("eevee_aggressive_01", EEVEE_AGGRESSIVE)
register_scene("eevee_heat_01", EEVEE_HEAT)


__all__ = [
    "EEVEE_INITIATE",
    "EEVEE_AGGRESSIVE", 
    "EEVEE_HEAT",
]
