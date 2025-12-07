"""
NPC System for Gilderhaven
===========================

Framework for creating interactive NPCs with:
- Dialogue trees (branching conversations)
- Schedules (movement between locations)
- Behaviors (reactions to events)
- Memory (tracks interactions per player)
- Shop/vendor functionality
- Special interactions (adult content)

Architecture:
- NPCs are Objects with npc_data attribute
- Dialogue is pure data (no code in conversations)
- Schedules driven by game time hooks
- Memory stored on NPC, keyed by character ID

Usage:
    from world.npcs import (
        create_npc, setup_npc, start_dialogue,
        get_npc_memory, set_npc_memory
    )
    
    # Create from template
    npc = create_npc("curator", location=museum_foyer)
    
    # Start conversation
    start_dialogue(player, npc)
    
    # Check memory
    if get_npc_memory(npc, player, "visited_office"):
        # Different dialogue
"""

import time
import random
from evennia import create_object, search_object
from evennia.utils import logger


# =============================================================================
# NPC Templates
# =============================================================================

NPC_TEMPLATES = {
    "curator": {
        "key": "The Curator",
        "aliases": ["curator"],
        "desc": """
The Curator stands before you - tall, blonde, possessed of a presence that
fills any room. Strong features soften only slightly when something catches
their interest, and right now that something might be you.

They dress impeccably in dark colors - professional but with hints of
something more beneath the surface. A silver chain hangs from their pocket,
and you notice their hands are both elegant and strong.

Their eyes miss nothing. When they focus on you, you feel catalogued,
appraised, and perhaps... selected.
""",
        "personality": {
            "dominant": True,
            "patient": True,
            "precise": True,
            "possessive": True,
            "caring": True,
        },
        "home_location": "Museum Foyer",
        "schedule": {
            "morning": "Curator's Office",
            "afternoon": "Grand Gallery",
            "evening": "Curator's Office",
            "night": "Curator's Private Chambers",
        },
        "dialogue_root": "curator_greeting",
        "shop_inventory": None,
        "flags": ["important", "dominant", "adult"],
    },
    
    "shopkeeper": {
        "key": "Friendly Shopkeeper",
        "aliases": ["shopkeeper", "merchant"],
        "desc": """
A cheerful figure stands behind the counter, ready to help with your
shopping needs. They have the practiced smile of someone who's seen
every kind of customer.
""",
        "personality": {
            "friendly": True,
            "mercantile": True,
        },
        "home_location": None,
        "schedule": None,
        "dialogue_root": "shopkeeper_greeting",
        "shop_inventory": "general",
        "flags": ["merchant"],
    },
    
    "guard": {
        "key": "Grove Guard",
        "aliases": ["guard"],
        "desc": """
A sturdy guard in simple armor keeps watch. They look alert but not
hostile - more protector than enforcer.
""",
        "personality": {
            "dutiful": True,
            "observant": True,
        },
        "home_location": None,
        "schedule": None,
        "dialogue_root": "guard_greeting",
        "shop_inventory": None,
        "flags": ["guard"],
    },
    
    "villager": {
        "key": "Grove Villager",
        "aliases": ["villager", "resident"],
        "desc": """
One of the Grove's many residents going about their day.
""",
        "personality": {
            "friendly": True,
        },
        "home_location": None,
        "schedule": None,
        "dialogue_root": "villager_greeting",
        "shop_inventory": None,
        "flags": ["ambient"],
    },
}


# =============================================================================
# Dialogue Trees
# =============================================================================

DIALOGUE_TREES = {
    # -------------------------------------------------------------------------
    # Curator Dialogues
    # -------------------------------------------------------------------------
    "curator_greeting": {
        "text": """
The Curator's gaze finds you, and for a moment you feel pinned in place
like a butterfly under glass.

"Welcome to my Museum." Their voice is warm but carries weight. "I trust
you'll treat my collection with the respect it deserves."

Their eyes move over you with clinical precision.

"Is there something I can help you with?"
""",
        "choices": [
            {
                "text": "Just looking around.",
                "next": "curator_just_looking",
            },
            {
                "text": "Tell me about the Museum.",
                "next": "curator_about_museum",
            },
            {
                "text": "Tell me about yourself.",
                "next": "curator_about_self",
            },
            {
                "text": "I should go.",
                "next": None,  # Ends conversation
                "exit_text": "The Curator nods. \"The Museum is always open. Return when you wish.\"",
            },
        ],
        "conditions": None,
    },
    
    "curator_just_looking": {
        "text": """
"Of course. Feel free to explore the public galleries." A slight smile
plays at the corner of their mouth.

"But do remember - I see everything that happens in my Museum. If you
have questions about any exhibits... or anything else... I'm always
available."

They pause, studying you.

"Some of my most interesting work isn't on public display."
""",
        "choices": [
            {
                "text": "What kind of work?",
                "next": "curator_private_work",
                "sets_flag": "curious_about_private",
            },
            {
                "text": "I'll keep that in mind.",
                "next": None,
                "exit_text": "\"See that you do.\" The Curator returns to their duties, though you sense their awareness of you doesn't fade.",
            },
        ],
    },
    
    "curator_about_museum": {
        "text": """
"The Museum houses artifacts and specimens from across the realms."
They gesture at the space around you. "Some beautiful. Some dangerous.
Some... both."

"I acquire pieces that deserve preservation. I study them. I display
them for those who can appreciate them."

Their eyes return to you.

"Every piece in my collection has a story. Every acquisition is
carefully considered. I don't take just anything."
""",
        "choices": [
            {
                "text": "How do you decide what to acquire?",
                "next": "curator_acquisition",
            },
            {
                "text": "What's the most interesting piece?",
                "next": "curator_favorite_piece",
            },
            {
                "text": "Thank you for explaining.",
                "next": "curator_greeting",
            },
        ],
    },
    
    "curator_about_self": {
        "text": """
"Myself?" A raised eyebrow. "I am the Curator. I have always been the
Curator. This Museum is my life's work."

They step closer, and you catch hints of their scent - leather, old
paper, something warmer underneath.

"I collect. I preserve. I... appreciate things of value." Their gaze
is very direct. "I recognize quality when I see it."

"Was there something specific you wanted to know?"
""",
        "choices": [
            {
                "text": "Do you live here?",
                "next": "curator_living_here",
            },
            {
                "text": "What do you do for fun?",
                "next": "curator_fun",
                "sets_flag": "asked_personal",
            },
            {
                "text": "Nothing specific. Thank you.",
                "next": "curator_greeting",
            },
        ],
    },
    
    "curator_private_work": {
        "text": """
"Restoration. Research. Private viewings for... select guests." Each
word is measured.

"There are areas of the Museum not open to the public. My office.
The archives. The restoration room." A beat. "My private chambers."

"Access to these spaces is by invitation only. I don't extend such
invitations lightly."

Their eyes hold yours.

"But I do extend them."
""",
        "choices": [
            {
                "text": "Are you inviting me?",
                "next": "curator_invitation_check",
                "requires_flag": "curious_about_private",
            },
            {
                "text": "What would I need to do for an invitation?",
                "next": "curator_earn_invitation",
            },
            {
                "text": "I'm not sure I'm ready for that.",
                "next": "curator_not_ready",
            },
        ],
    },
    
    "curator_invitation_check": {
        "text": """
The Curator studies you for a long moment. You feel weighed. Measured.

"Perhaps." The word hangs in the air. "You seem... curious. Curiosity
is valuable. But so is patience."

They produce a small card from their pocket - cream paper, elegant script.

"This grants you access to my office. Come when you're ready. We can
discuss... possibilities."
""",
        "choices": [
            {
                "text": "Accept the card.",
                "next": None,
                "sets_flag": "has_office_access",
                "exit_text": """
Their fingers brush yours as you take the card, a deliberate touch.

"Good." Simple. Pleased. "I'll be waiting."

They step back, the professional distance restored, but something has
shifted between you.
""",
            },
            {
                "text": "I need to think about it.",
                "next": None,
                "exit_text": """
"Of course." The card disappears back into their pocket. "The invitation
remains open. I'm patient."

A slight smile.

"But I do so enjoy when my patience is rewarded."
""",
            },
        ],
    },
    
    "curator_earn_invitation": {
        "text": """
"Do?" A low laugh. "This isn't a transaction. I don't barter access
to my private spaces."

They move closer, and you resist the urge to step back.

"I invite people who interest me. Who show... potential. Who understand
that some experiences require trust." Their voice drops. "And surrender."

"Show me who you are. What you want. What you're capable of accepting."

"Then we'll see."
""",
        "choices": [
            {
                "text": "What kind of surrender?",
                "next": "curator_explain_surrender",
                "sets_flag": "asked_about_surrender",
            },
            {
                "text": "I understand.",
                "next": None,
                "exit_text": "\"Do you?\" The question lingers as the Curator returns to their work. You suspect you've only begun to understand.",
            },
        ],
    },
    
    "curator_explain_surrender": {
        "text": """
The Curator's expression shifts - still controlled, but something
deeper surfaces.

"Control is a gift. To give it... and to receive it." They speak
quietly now, for you alone.

"In my private spaces, I am in charge. Completely. Those who enter
accept that. In return, I provide structure. Safety. Purpose."

A pause.

"I take what is offered freely. I hold it with absolute care. I
return it transformed."

"This is not for everyone. But for some... it is exactly what they need."
""",
        "choices": [
            {
                "text": "That sounds like what I need.",
                "next": "curator_invitation_check",
                "sets_flag": "expressed_interest",
            },
            {
                "text": "I need time to think.",
                "next": None,
                "sets_flag": "considering",
                "exit_text": """
"Take all the time you need." Gentle now. Understanding.

"When you're ready - if you're ever ready - I'll be here."

They touch your cheek, brief and warm.

"Some things are worth waiting for."
""",
            },
        ],
    },
    
    "curator_not_ready": {
        "text": """
"Honesty." They nod, approving. "That's valuable too."

"Not everyone is suited for what I offer. Not everyone wants it. There's
no shame in knowing yourself."

The professional distance returns, but their voice remains warm.

"Enjoy the public galleries. The collection is worth seeing regardless.
And should your... readiness... change, the offer remains."
""",
        "choices": [
            {
                "text": "Thank you for understanding.",
                "next": None,
                "exit_text": "The Curator inclines their head. \"Understanding is part of what I do.\" They move away, but you sense the door hasn't closed entirely.",
            },
        ],
    },
    
    "curator_living_here": {
        "text": """
"I have chambers in the Museum, yes. Private. Comfortable." A slight
smile. "Equipped for my particular needs."

"The Museum never truly closes for me. I walk the galleries at night.
I work in my office at all hours. This place is as much a part of me
as I am of it."

"Why do you ask? Curious where the Curator sleeps?"
""",
        "choices": [
            {
                "text": "Maybe a little curious.",
                "next": "curator_private_work",
                "sets_flag": "curious_about_private",
            },
            {
                "text": "Just making conversation.",
                "next": "curator_greeting",
            },
        ],
    },
    
    "curator_fun": {
        "text": """
"Fun?" They consider the word as if tasting it.

"I find satisfaction in my work. In acquiring something perfect. In
the moment a new piece finds its place in my collection."

A pause. Their eyes darken slightly.

"I enjoy... training. Taking something rough and revealing its
potential. Watching someone discover what they're capable of."

"That's fun enough for me."
""",
        "choices": [
            {
                "text": "Training? What kind of training?",
                "next": "curator_explain_surrender",
                "sets_flag": "asked_about_training",
            },
            {
                "text": "You have interesting hobbies.",
                "next": None,
                "exit_text": "\"I have interesting everything.\" The Curator's smile holds secrets. \"Come back when you want to learn more.\"",
            },
        ],
    },
    
    "curator_acquisition": {
        "text": """
"Every piece must earn its place." The Curator's voice takes on a
professional tone. "Provenance. Condition. Significance."

"But also... resonance. Some things simply belong here. I know it
when I see it."

Their gaze lingers on you.

"The same applies to people, incidentally. Some belong in certain
places. With certain... curators."
""",
        "choices": [
            {
                "text": "Are you saying I belong here?",
                "next": "curator_private_work",
                "sets_flag": "curious_about_private",
            },
            {
                "text": "Interesting perspective.",
                "next": "curator_greeting",
            },
        ],
    },
    
    "curator_favorite_piece": {
        "text": """
"Favorites?" They pause, genuinely considering. "The transformation
specimens in Natural History are remarkable. The cursed items in
Curiosities are fascinating."

"But my true favorites aren't on display." A knowing look. "Some
things are too precious - or too dangerous - for public viewing."

"Perhaps someday you'll see them."
""",
        "choices": [
            {
                "text": "I'd like that.",
                "next": "curator_private_work",
                "sets_flag": "curious_about_private",
            },
            {
                "text": "Maybe someday.",
                "next": "curator_greeting",
            },
        ],
    },
    
    # -------------------------------------------------------------------------
    # Curator Office Dialogues (when player has card)
    # -------------------------------------------------------------------------
    "curator_office_greeting": {
        "text": """
The Curator looks up from their desk as you enter. Something shifts in
their expression - not surprise, but... satisfaction.

"You came." They rise, moving around the desk with deliberate grace.
"Close the door."

It's not a request.

They gesture to the space before them - the low chair, the cushion
beside it.

"Sit. Or kneel. Your choice tells me something about you."
""",
        "choices": [
            {
                "text": "Sit in the chair.",
                "next": "curator_office_chair",
            },
            {
                "text": "Kneel on the cushion.",
                "next": "curator_office_kneel",
                "sets_flag": "chose_to_kneel",
            },
            {
                "text": "I'll stand.",
                "next": "curator_office_stand",
            },
        ],
        "conditions": {"location": "Curator's Office"},
    },
    
    "curator_office_chair": {
        "text": """
You settle into the low chair. Even seated, you have to look up at
the Curator. The furniture was designed this way.

They return to their seat behind the desk, watching you over steepled
fingers.

"Comfortable? Good. We should talk about why you're here."

A pause.

"You accepted my invitation. That means you're curious. Curious about
me. About what I offer. About what you might want."

"So. What do you want?"
""",
        "choices": [
            {
                "text": "I'm not entirely sure yet.",
                "next": "curator_office_uncertain",
            },
            {
                "text": "I want to know more about... what you mentioned.",
                "next": "curator_office_explain",
            },
            {
                "text": "I think I want what you described. Control. Structure.",
                "next": "curator_office_direct",
                "sets_flag": "expressed_desire",
            },
        ],
    },
    
    "curator_office_kneel": {
        "text": """
You sink to your knees on the velvet cushion. It's softer than you
expected. The position feels... right, somehow.

The Curator watches you settle, and something warm enters their eyes.

"Good." The word lands like a hand on your head. "That tells me quite
a lot."

They remain standing, looking down at you. One hand reaches out,
fingertips brushing your chin, tilting your face up.

"You have good instincts. Now tell me - what brought you to your
knees just now? Curiosity? Desire? Or did it simply feel like where
you belonged?"
""",
        "choices": [
            {
                "text": "It felt right.",
                "next": "curator_office_felt_right",
                "sets_flag": "admitted_submission",
            },
            {
                "text": "I wanted to show respect.",
                "next": "curator_office_uncertain",
            },
            {
                "text": "I'm not sure. I just... did.",
                "next": "curator_office_felt_right",
                "sets_flag": "natural_instinct",
            },
        ],
    },
    
    "curator_office_stand": {
        "text": """
You remain standing. The Curator's eyebrow rises slightly.

"Independent. That's not a bad thing." They circle you slowly, and
you resist the urge to turn and track their movement.

"Some people need to be... convinced. To find their surrender
gradually, rather than offering it freely."

They stop in front of you, closer than strictly necessary.

"I can work with that. The question is whether you want me to."
""",
        "choices": [
            {
                "text": "What would that look like?",
                "next": "curator_office_explain",
            },
            {
                "text": "I'm still figuring out what I want.",
                "next": "curator_office_uncertain",
            },
            {
                "text": "Maybe I do want that.",
                "next": "curator_office_direct",
                "sets_flag": "expressed_desire",
            },
        ],
    },
    
    "curator_office_uncertain": {
        "text": """
"Uncertainty is honest. I appreciate that." The Curator's voice
gentles slightly.

"Let me be clear about what I offer, and what I expect."

They lean against the desk, arms crossed.

"I provide structure. Direction. For some people, that's exactly what
they need - someone to take the decisions away, at least for a time.
Someone to hold them accountable. Someone to..."

A slight smile.

"...take care of them. In my particular way."

"In return, I expect honesty. Communication. And when you're mine -
obedience."

"This isn't for everyone. That's fine. But if it calls to something
in you... we can explore that. Slowly. Safely."
""",
        "choices": [
            {
                "text": "What do you mean by 'mine'?",
                "next": "curator_office_ownership",
            },
            {
                "text": "How would we start?",
                "next": "curator_office_beginning",
                "sets_flag": "wants_to_begin",
            },
            {
                "text": "I need more time to think.",
                "next": "curator_office_time",
            },
        ],
    },
    
    "curator_office_explain": {
        "text": """
"What I offer is a dynamic. A relationship with clear roles."

The Curator's voice takes on a teaching quality, though the intensity
never leaves their eyes.

"I am dominant. I lead. I decide. I take responsibility for those
in my care."

"Those who submit to me... they give me their trust. Their control.
Their obedience. In return, I provide safety, structure, growth."

"I will push you. Challenge you. Hold you to standards. I will also
protect you, guide you, and yes - reward you when you've earned it."

They step closer.

"I don't share. I don't tolerate deception. And I don't make promises
I can't keep."

"Does this frighten you? Or excite you?"
""",
        "choices": [
            {
                "text": "Both.",
                "next": "curator_office_both",
                "sets_flag": "honest_response",
            },
            {
                "text": "It excites me.",
                "next": "curator_office_direct",
                "sets_flag": "expressed_desire",
            },
            {
                "text": "I'm not sure I can give that much control.",
                "next": "curator_office_uncertain",
            },
        ],
    },
    
    "curator_office_direct": {
        "text": """
The Curator's expression sharpens with interest.

"Direct. I like that." They move closer, into your space. You can
smell leather, old paper, warmth.

"You think you want this. Let's find out if you're right."

Their hand cups your jaw, firm but not painful. Their eyes hold yours.

"If we do this - if you become mine - there are rules. Expectations.
You will address me with respect. You will be honest, always. You
will obey, or you will explain why you cannot."

"In return, I will take care of you. Push you. Grow you. Make you
more than you are now."

"This is not a game. This is real. Do you understand?"
""",
        "choices": [
            {
                "text": "Yes. I understand.",
                "next": "curator_office_accept",
                "sets_flag": "accepted_dynamic",
            },
            {
                "text": "I want this, but I'm scared.",
                "next": "curator_office_both",
            },
            {
                "text": "What happens if I say yes?",
                "next": "curator_office_beginning",
            },
        ],
    },
    
    "curator_office_felt_right": {
        "text": """
"It felt right." The Curator repeats your words, tasting them.

Their fingers are still under your chin, holding your gaze.

"Because it is right. For you. Some people are built for this - built
to kneel, to serve, to find peace in surrender."

"I recognized it in you when you first walked into my Museum. That
hunger for something you couldn't name."

They crouch down, bringing themselves to your eye level. Their face
is close now.

"I can give it a name. I can give it structure. I can give you a
place to belong."

"Do you want that?"
""",
        "choices": [
            {
                "text": "Yes.",
                "next": "curator_office_accept",
                "sets_flag": "accepted_dynamic",
            },
            {
                "text": "I think so. Yes.",
                "next": "curator_office_accept",
                "sets_flag": "accepted_dynamic",
            },
            {
                "text": "What would that mean, exactly?",
                "next": "curator_office_explain",
            },
        ],
    },
    
    "curator_office_ownership": {
        "text": """
"Mine." The word carries weight when they say it.

"Ownership is not slavery. It's not about taking away who you are.
It's about holding what you choose to give."

"When you're mine, your pleasure belongs to me. Your growth belongs
to me. Your submission belongs to me."

"I will know you. Train you. Shape you. Not into something false -
into the truest version of yourself."

Their voice drops.

"And you will be cared for. Protected. Valued. Because things that
belong to me... I take very good care of."
""",
        "choices": [
            {
                "text": "That sounds like what I've been looking for.",
                "next": "curator_office_direct",
                "sets_flag": "expressed_desire",
            },
            {
                "text": "How long would this last?",
                "next": "curator_office_beginning",
            },
            {
                "text": "I need to think about this.",
                "next": "curator_office_time",
            },
        ],
    },
    
    "curator_office_beginning": {
        "text": """
"How would we start?" A pleased smile crosses their face.

"Slowly. Carefully. Trust is built, not demanded."

"First, we talk. Like this. You tell me your fears, your desires,
your limits. I tell you my expectations."

"Then, small things. Tasks. Rituals. Ways for you to practice giving
control, and for me to practice holding it."

"As trust grows, so does depth. More is given. More is expected.
Until eventually..."

They trail off, letting the implication hang.

"But that's getting ahead of ourselves. Right now, I just need to
know - do you want to try?"
""",
        "choices": [
            {
                "text": "Yes. I want to try.",
                "next": "curator_office_accept",
                "sets_flag": "accepted_dynamic",
            },
            {
                "text": "What kind of tasks?",
                "next": "curator_office_explain",
            },
            {
                "text": "What are your expectations?",
                "next": "curator_office_explain",
            },
        ],
    },
    
    "curator_office_accept": {
        "text": """
Something shifts in the Curator's expression. Satisfaction. Warmth.
Hunger, carefully controlled.

"Good." The word is a caress.

They reach out, hand settling on top of your head. The touch is
proprietary. Claiming.

"Then let's begin. From now on, when we're alone, you will address
me as 'Curator' or 'Ma'am'. You will answer honestly. You will tell
me if something is too much."

"In return, I will guide you. Push you. Take care of you."

Their hand slides down to cup your cheek.

"Welcome to my collection, little one. I'm going to enjoy this."
""",
        "choices": [
            {
                "text": "Yes, Curator.",
                "next": None,
                "sets_flag": "dynamic_established",
                "exit_text": """
A genuine smile breaks across their face - the first you've seen
that reaches their eyes.

"Perfect. We're going to do wonderful things together."

They release you, stepping back, the professional mask sliding
back into place.

"Go now. Return tomorrow. We'll start your training properly."

"And remember - I see everything. Make me proud."
""",
            },
            {
                "text": "Thank you, Curator.",
                "next": None,
                "sets_flag": "dynamic_established",
                "exit_text": """
"Gratitude already. You learn quickly." Their voice is warm.

They help you to your feet, hands lingering.

"Go rest. Think about what you've agreed to. Tomorrow, we begin
in earnest."

"And little one?" They catch your chin one more time. "I'm pleased
you came to me."
""",
            },
        ],
    },
    
    "curator_office_time": {
        "text": """
"Of course." No disappointment in their voice. "This isn't a decision
to make lightly."

They step back, giving you space.

"Take all the time you need. Think about what you want. What you
fear. What you might need."

"My door remains open. When you're ready - if you're ready - I'll
be here."

A slight smile.

"Some things are worth waiting for. I'm patient. And I think you
might be worth waiting for."
""",
        "choices": [
            {
                "text": "Thank you for understanding.",
                "next": None,
                "exit_text": "The Curator inclines their head gracefully. \"Understanding is part of what I do. Go. Return when you're ready.\"",
            },
        ],
    },
    
    "curator_office_both": {
        "text": """
"Both." They nod, approving. "That's the right answer."

"Fear and excitement together - that's how you know something matters.
Something that leaves you completely calm? Not worth pursuing."

"The fear will fade as trust builds. The excitement..." A slight
smile. "That tends to grow."

They study you carefully.

"You're more ready than you think. The question is whether you're
willing to find out."
""",
        "choices": [
            {
                "text": "I'm willing.",
                "next": "curator_office_direct",
                "sets_flag": "expressed_desire",
            },
            {
                "text": "How do I know if I'm ready?",
                "next": "curator_office_ready",
            },
        ],
    },
    
    "curator_office_ready": {
        "text": """
"You're ready when you can answer three questions honestly."

The Curator counts on their fingers.

"One: Do you want this? Not 'should I' or 'is it okay to' - do you
actually want it?"

"Two: Can you communicate? Tell me when something is wrong, when
you're struggling, when you need more or less?"

"Three: Do you trust me enough to try? Not complete trust - that
comes later. Just enough to take the first step."

They spread their hands.

"Can you answer yes to those three things?"
""",
        "choices": [
            {
                "text": "Yes. Yes to all three.",
                "next": "curator_office_accept",
                "sets_flag": "accepted_dynamic",
            },
            {
                "text": "I want to, but I'm not sure about trust yet.",
                "next": "curator_office_trust_building",
            },
            {
                "text": "I need to think.",
                "next": "curator_office_time",
            },
        ],
    },
    
    "curator_office_trust_building": {
        "text": """
"Trust is earned. I don't expect you to hand it over blindly."

The Curator's voice is patient.

"We can build it. Slowly. Small steps before large ones."

"Come to me. Spend time. Let me show you who I am through actions,
not just words. Ask questions. Watch how I treat others."

"When you're ready to take the step... you'll know."

They offer their hand.

"For now - would you like to stay awhile? No pressure. Just... 
company. You can ask me anything."
""",
        "choices": [
            {
                "text": "I'd like that.",
                "next": None,
                "sets_flag": "building_trust",
                "exit_text": """
The Curator's smile is warm. "Good. Sit with me. Tell me about
yourself. Let's start there."

They settle into conversation, and for once, the intensity
softens into something almost comfortable.

The beginning of something, perhaps.
""",
            },
            {
                "text": "I should go. But I'll come back.",
                "next": None,
                "sets_flag": "will_return",
                "exit_text": """
"I'll be here." Simple. Certain.

They walk you to the door, a hand briefly on the small of your
back.

"Take care of yourself. And... I'm glad you came."
""",
            },
        ],
    },
    
    # -------------------------------------------------------------------------
    # Curator Context-Aware Greetings
    # -------------------------------------------------------------------------
    "curator_has_card_greeting": {
        "text": """
The Curator's eyes find yours across the gallery. A slight smile
curves their lips as they approach.

"You still have my card, I see." Their voice is low, for you alone.
"It's not a souvenir. It's an invitation."

They lean closer, breath warm against your ear.

"Come to my office. We have things to discuss... in private."

They step back, professional mask in place, as if nothing happened.
""",
        "choices": [
            {
                "text": "I'll come now.",
                "next": None,
                "exit_text": "\"Good.\" Simple. Pleased. \"I'll be waiting.\" They turn and walk toward the staff door, not looking back. They know you'll follow.",
            },
            {
                "text": "I'm still thinking about it.",
                "next": None,
                "exit_text": "\"Don't think too long.\" A slight edge beneath the warmth. \"Invitations aren't extended forever.\" They move away, leaving you with the weight of the card in your pocket.",
            },
            {
                "text": "I wanted to see you first.",
                "next": "curator_wanted_to_see",
            },
        ],
    },
    
    "curator_wanted_to_see": {
        "text": """
Something flickers in the Curator's expression. Surprise? Pleasure?

"Wanted to see me." They taste the words. "Not the collection. Not
the galleries. Me."

They step into your space again, shameless about the intimacy in
a public place.

"Careful. Wanting things is how people end up in my collection."

But their eyes are warm.

"Go to my office. I'll finish here and join you. We can... talk."
""",
        "choices": [
            {
                "text": "Yes, Curator.",
                "next": None,
                "sets_flag": "used_title_early",
                "exit_text": """
Their breath catches. Just slightly. But you notice.

"Already learning." Warmth and hunger, tightly controlled.

"Go. Now. Before I do something inappropriate in my own gallery."

They turn away, but not before you catch the edge of a genuine smile.
""",
            },
            {
                "text": "I'll wait for you there.",
                "next": None,
                "exit_text": "\"Do that.\" Their hand brushes yours as they pass - brief, electric, deliberate. \"I won't be long.\"",
            },
        ],
    },
    
    # -------------------------------------------------------------------------
    # Generic NPC Dialogues
    # -------------------------------------------------------------------------
    "shopkeeper_greeting": {
        "text": """
"Welcome! Take a look around - I've got a bit of everything. Let me
know if you need help finding anything specific."
""",
        "choices": [
            {
                "text": "What do you have for sale?",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "Just browsing.",
                "next": None,
                "exit_text": "\"Take your time! I'll be here.\"",
            },
        ],
    },
    
    "guard_greeting": {
        "text": """
"Citizen." The guard nods. "Keeping safe, I hope. Let me know if
you see any trouble."
""",
        "choices": [
            {
                "text": "Everything's fine.",
                "next": None,
                "exit_text": "\"Good to hear. Stay safe.\"",
            },
            {
                "text": "What should I watch out for?",
                "next": "guard_warnings",
            },
        ],
    },
    
    "guard_warnings": {
        "text": """
"The Grove is mostly safe, but the wild areas can be dangerous.
Whisperwood has slimes. Copper Hill has unstable tunnels. The deep
water at Moonshallow has pulled people under."

"Stay on the paths, don't touch things that glow, and you'll be fine."
""",
        "choices": [
            {
                "text": "Thanks for the warning.",
                "next": None,
                "exit_text": "\"That's what I'm here for. Be safe out there.\"",
            },
        ],
    },
    
    "villager_greeting": {
        "text": """
"Oh, hello there! Nice day, isn't it?"
""",
        "choices": [
            {
                "text": "Beautiful day.",
                "next": None,
                "exit_text": "\"It really is! Well, take care!\"",
            },
            {
                "text": "Have you lived here long?",
                "next": "villager_history",
            },
        ],
    },
    
    "villager_history": {
        "text": """
"Born and raised! The Grove's a good place. Safe. Friendly. A little
strange sometimes, but that's part of the charm."

"If you're new, make sure to visit the Museum. The Curator's... intense,
but the collection is worth seeing."
""",
        "choices": [
            {
                "text": "Thanks for the tip!",
                "next": None,
                "exit_text": "\"Anytime! Welcome to the Grove!\"",
            },
        ],
    },
    
    # -------------------------------------------------------------------------
    # Shopkeeper Dialogues
    # -------------------------------------------------------------------------
    "tool_vendor_greeting": {
        "text": """
"Good tools make good work." The vendor sets down a file and looks
up at you. "I've got the best in the Grove - fishing rods, pickaxes,
nets, baskets. All hand-crafted."

"What do you need?"
""",
        "choices": [
            {
                "text": "Show me your tools.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "What's your best equipment?",
                "next": "tool_vendor_best",
            },
            {
                "text": "Just browsing.",
                "next": None,
                "exit_text": "\"Take a look around. Quality speaks for itself.\"",
            },
        ],
    },
    
    "tool_vendor_best": {
        "text": """
"Ah, you want the good stuff." They lean in conspiratorially.

"I've got master-quality tools - fishing rods that practically catch
fish themselves, pickaxes that bite through stone like butter. Not
cheap, mind you, but they last forever and work twice as well."

"The basic gear will get you started, but if you're serious about
gathering... you want the master tier."
""",
        "choices": [
            {
                "text": "Show me everything.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "I'll start with basic gear.",
                "next": None,
                "action": "open_shop",
            },
        ],
    },
    
    "apothecary_greeting": {
        "text": """
The apothecary looks up from a bubbling concoction.

"Hmm? Oh, a customer. Yes, yes." They wave vaguely at the shelves.
"Potions, medicines, remedies. Health, stamina, cures for various...
afflictions."

They peer at you over their spectacles.

"What ails you?"
""",
        "choices": [
            {
                "text": "I need healing potions.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "Do you have anything... special?",
                "next": "apothecary_special",
            },
            {
                "text": "Nothing right now.",
                "next": None,
                "exit_text": "\"Mm. Come back when something ails you. Something always does, eventually.\"",
            },
        ],
    },
    
    "apothecary_special": {
        "text": """
The apothecary's eyebrows rise slightly.

"Special? I have... a few things. Not on the main shelves."

They glance around and lower their voice.

"Aphrodisiacs. Sensitivity enhancers. Things for... adult pursuits.
All perfectly safe, mind you. Just... discreet."

"Interested?"
""",
        "choices": [
            {
                "text": "Show me everything, including those.",
                "next": None,
                "action": "open_shop_adult",
            },
            {
                "text": "Just the regular potions, please.",
                "next": None,
                "action": "open_shop",
            },
        ],
    },
    
    "tavern_greeting": {
        "text": """
"What'll it be?" The tavern keeper sets down a glass and looks at
you expectantly.

"Got ale, got food, got a warm fire. Not much else, but what else
do you need?"
""",
        "choices": [
            {
                "text": "I'll take some food and drink.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "Just passing through.",
                "next": None,
                "exit_text": "\"Suit yourself. Door's always open.\"",
            },
        ],
    },
    
    "buyer_greeting": {
        "text": """
The trader looks up from examining a gemstone.

"You have materials to sell? I buy ore, herbs, fish, shells -
anything raw that craftspeople need."

They set down the loupe.

"I pay fair prices. Better than most. What have you got?"
""",
        "choices": [
            {
                "text": "Let me show you what I have.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "What pays the best?",
                "next": "buyer_best",
            },
            {
                "text": "Nothing right now.",
                "next": None,
                "exit_text": "\"Come back when your pockets are full. I'll be here.\"",
            },
        ],
    },
    
    "buyer_best": {
        "text": """
"Best prices?" They tick off on their fingers.

"Ore - especially silver and gold. Gems, always. Pearls from the
river. Rare moths and butterflies fetch good coin too."

"The common stuff - berries, basic fish, shells - I'll take it, but
don't expect to get rich on it."

"Find me the rare materials and we'll both do well."
""",
        "choices": [
            {
                "text": "Let's see what I can sell.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "Good to know. I'll be back.",
                "next": None,
                "exit_text": "\"Looking forward to it. Good hunting.\"",
            },
        ],
    },
}


# =============================================================================
# Core NPC Functions
# =============================================================================

def create_npc(template_key, location=None, typeclass="typeclasses.characters.Character"):
    """
    Create an NPC from a template.
    
    Args:
        template_key: Key in NPC_TEMPLATES
        location: Where to place the NPC
        typeclass: Typeclass to use (default: Character so they show in rooms)
    
    Returns:
        Object: The created NPC
    """
    template = NPC_TEMPLATES.get(template_key)
    if not template:
        logger.log_err(f"Unknown NPC template: {template_key}")
        return None
    
    npc = create_object(
        typeclass,
        key=template["key"],
        location=location,
    )
    
    # Set up NPC data
    npc.db.desc = template.get("desc", "").strip()
    npc.db.npc_template = template_key
    npc.db.npc_data = {
        "personality": template.get("personality", {}),
        "home_location": template.get("home_location"),
        "schedule": template.get("schedule"),
        "dialogue_root": template.get("dialogue_root"),
        "shop_inventory": template.get("shop_inventory"),
        "flags": template.get("flags", []),
    }
    npc.db.npc_memory = {}  # Per-character memory
    npc.db.npc_state = {
        "current_activity": "idle",
        "last_interaction": None,
    }
    
    # Add aliases
    if template.get("aliases"):
        npc.aliases.add(template["aliases"])
    
    # Tag as NPC
    npc.tags.add("npc", category="object_type")
    for flag in template.get("flags", []):
        npc.tags.add(flag, category="npc_flag")
    
    return npc


def setup_npc(obj, template_key):
    """
    Set up an existing object as an NPC.
    
    Args:
        obj: Object to configure
        template_key: Template to apply
    """
    template = NPC_TEMPLATES.get(template_key)
    if not template:
        return False
    
    obj.db.desc = template.get("desc", "").strip()
    obj.db.npc_template = template_key
    obj.db.npc_data = {
        "personality": template.get("personality", {}),
        "home_location": template.get("home_location"),
        "schedule": template.get("schedule"),
        "dialogue_root": template.get("dialogue_root"),
        "shop_inventory": template.get("shop_inventory"),
        "flags": template.get("flags", []),
    }
    obj.db.npc_memory = {}
    obj.db.npc_state = {"current_activity": "idle"}
    
    obj.tags.add("npc", category="object_type")
    return True


def is_npc(obj):
    """Check if an object is an NPC."""
    return obj.tags.has("npc", category="object_type")


def get_npc_data(npc):
    """Get NPC's data dict."""
    return npc.db.npc_data or {}


# =============================================================================
# NPC Memory
# =============================================================================

def get_npc_memory(npc, character, key=None):
    """
    Get NPC's memory about a specific character.
    
    Args:
        npc: The NPC
        character: Character to get memory about
        key: Specific memory key, or None for all
    
    Returns:
        Value of specific key, or full memory dict
    """
    memory = npc.db.npc_memory or {}
    char_memory = memory.get(character.id, {})
    
    if key:
        return char_memory.get(key)
    return char_memory


def set_npc_memory(npc, character, key, value):
    """
    Set NPC's memory about a character.
    
    Args:
        npc: The NPC
        character: Character to remember
        key: Memory key
        value: Value to store
    """
    if not npc.db.npc_memory:
        npc.db.npc_memory = {}
    
    if character.id not in npc.db.npc_memory:
        npc.db.npc_memory[character.id] = {}
    
    npc.db.npc_memory[character.id][key] = value


def has_npc_flag(npc, character, flag):
    """Check if NPC has set a flag for this character."""
    return get_npc_memory(npc, character, flag) is True


def set_npc_flag(npc, character, flag):
    """Set a flag in NPC's memory for this character."""
    set_npc_memory(npc, character, flag, True)


def clear_npc_flag(npc, character, flag):
    """Clear a flag from NPC's memory."""
    memory = npc.db.npc_memory or {}
    char_memory = memory.get(character.id, {})
    if flag in char_memory:
        del char_memory[flag]


# =============================================================================
# Dialogue System
# =============================================================================

def get_dialogue_node(node_key):
    """Get a dialogue node by key."""
    return DIALOGUE_TREES.get(node_key)


def start_dialogue(character, npc, node_key=None):
    """
    Start a dialogue with an NPC.
    
    Args:
        character: Character initiating
        npc: NPC to talk to
        node_key: Starting node (or use NPC's default, modified by context)
    
    Returns:
        bool: Success
    """
    if not is_npc(npc):
        character.msg(f"{npc.key} doesn't seem interested in talking.")
        return False
    
    npc_data = get_npc_data(npc)
    
    # Get starting node - check context if not specified
    if not node_key:
        node_key = get_contextual_dialogue(character, npc)
    
    if not node_key:
        node_key = npc_data.get("dialogue_root")
    
    if not node_key:
        character.msg(f"{npc.key} has nothing to say.")
        return False
    
    node = get_dialogue_node(node_key)
    if not node:
        character.msg(f"{npc.key} seems confused.")
        return False
    
    # Store dialogue state
    character.db.in_dialogue = {
        "npc_id": npc.id,
        "current_node": node_key,
        "started": time.time(),
    }
    
    # Update NPC state
    npc.db.npc_state["last_interaction"] = time.time()
    npc.db.npc_state["talking_to"] = character.id
    
    # Display the dialogue
    display_dialogue_node(character, npc, node)
    
    return True


def get_contextual_dialogue(character, npc):
    """
    Get the appropriate dialogue based on context.
    
    Checks location, flags, and other conditions to determine
    which dialogue tree to start.
    
    Args:
        character: The player
        npc: The NPC
    
    Returns:
        str: Dialogue node key or None for default
    """
    npc_data = get_npc_data(npc)
    template = npc.db.npc_template
    
    # Curator-specific context
    if template == "curator":
        location = character.location
        
        # In the office with access
        if location and "Office" in location.key:
            if has_npc_flag(npc, character, "has_office_access"):
                # Already established dynamic
                if has_npc_flag(npc, character, "dynamic_established"):
                    return "curator_office_return"  # TODO: Add this
                return "curator_office_greeting"
        
        # In private chambers (if ever accessible)
        if location and "Private" in location.key:
            if has_npc_flag(npc, character, "dynamic_established"):
                return "curator_private_greeting"  # TODO: Add this
        
        # Already has card but in public area
        if has_npc_flag(npc, character, "has_office_access"):
            return "curator_has_card_greeting"
    
    return None


def display_dialogue_node(character, npc, node):
    """
    Display a dialogue node to the character.
    
    Args:
        character: Who to display to
        npc: NPC speaking
        node: Dialogue node dict
    """
    # Display NPC's text
    text = node.get("text", "").strip()
    character.msg(f"\n|c{npc.key}|n\n{text}\n")
    
    # Display choices
    choices = node.get("choices", [])
    valid_choices = []
    
    for i, choice in enumerate(choices):
        # Check requirements
        if choice.get("requires_flag"):
            if not has_npc_flag(npc, character, choice["requires_flag"]):
                continue
        
        valid_choices.append((i + 1, choice))
    
    if valid_choices:
        character.msg("|yChoices:|n")
        for num, choice in valid_choices:
            character.msg(f"  |w{num}|n. {choice['text']}")
        character.msg("|x(Type the number of your choice)|n")
    else:
        # No choices means end of conversation
        end_dialogue(character)


def process_dialogue_choice(character, choice_num):
    """
    Process a dialogue choice.
    
    Args:
        character: Character making choice
        choice_num: Number of the choice (1-indexed)
    
    Returns:
        bool: Success
    """
    dialogue_state = character.db.in_dialogue
    if not dialogue_state:
        return False
    
    # Get NPC
    try:
        from evennia.objects.models import ObjectDB
        npc = ObjectDB.objects.get(id=dialogue_state["npc_id"])
    except:
        end_dialogue(character)
        return False
    
    # Get current node
    node = get_dialogue_node(dialogue_state["current_node"])
    if not node:
        end_dialogue(character)
        return False
    
    # Get valid choices
    choices = node.get("choices", [])
    valid_choices = []
    
    for choice in choices:
        if choice.get("requires_flag"):
            if not has_npc_flag(npc, character, choice["requires_flag"]):
                continue
        valid_choices.append(choice)
    
    # Validate choice number
    if choice_num < 1 or choice_num > len(valid_choices):
        character.msg("Invalid choice. Please pick a number from the list.")
        return False
    
    choice = valid_choices[choice_num - 1]
    
    # Process choice effects
    if choice.get("sets_flag"):
        set_npc_flag(npc, character, choice["sets_flag"])
    
    if choice.get("action"):
        handle_dialogue_action(character, npc, choice["action"])
    
    # Show exit text if ending
    if choice.get("next") is None:
        if choice.get("exit_text"):
            character.msg(f"\n{choice['exit_text'].strip()}\n")
        end_dialogue(character)
        return True
    
    # Move to next node
    next_node = get_dialogue_node(choice["next"])
    if not next_node:
        character.msg(f"{npc.key} seems to lose their train of thought.")
        end_dialogue(character)
        return False
    
    dialogue_state["current_node"] = choice["next"]
    display_dialogue_node(character, npc, next_node)
    
    return True


def handle_dialogue_action(character, npc, action):
    """
    Handle special dialogue actions.
    
    Args:
        character: Character
        npc: NPC
        action: Action string
    """
    if action == "open_shop":
        # Open shop interface
        try:
            from world.shops import is_shop, open_shop
            if is_shop(npc):
                open_shop(character, npc)
            else:
                character.msg(f"|y{npc.key} doesn't have anything for sale.|n")
        except ImportError:
            character.msg("|yShop system not available.|n")
    
    elif action == "open_shop_adult":
        # Open shop with adult items visible
        try:
            from world.shops import is_shop, open_shop
            if is_shop(npc):
                character.db.show_adult_content = True
                open_shop(character, npc)
            else:
                character.msg(f"|y{npc.key} doesn't have anything for sale.|n")
        except ImportError:
            character.msg("|yShop system not available.|n")
    
    elif action == "give_item":
        # STUB: Give item to character
        pass
    
    elif action == "start_scene":
        # STUB: Trigger a scene
        pass


def end_dialogue(character):
    """
    End a dialogue session.
    
    Args:
        character: Character to end dialogue for
    """
    dialogue_state = character.db.in_dialogue
    if dialogue_state:
        # Clear NPC's talking state
        try:
            from evennia.objects.models import ObjectDB
            npc = ObjectDB.objects.get(id=dialogue_state["npc_id"])
            if npc.db.npc_state:
                npc.db.npc_state["talking_to"] = None
        except:
            pass
    
    character.db.in_dialogue = None


def is_in_dialogue(character):
    """Check if character is in a dialogue."""
    return character.db.in_dialogue is not None


# =============================================================================
# NPC Behaviors
# =============================================================================

def npc_ambient_action(npc):
    """
    Generate an ambient action for an NPC.
    
    Args:
        npc: The NPC
    
    Returns:
        str: Action message or None
    """
    npc_data = get_npc_data(npc)
    personality = npc_data.get("personality", {})
    
    actions = [
        f"{npc.key} looks around the room.",
        f"{npc.key} shifts their weight slightly.",
    ]
    
    if personality.get("dominant"):
        actions.extend([
            f"{npc.key}'s gaze sweeps the room, missing nothing.",
            f"{npc.key} watches you with quiet intensity.",
        ])
    
    if personality.get("friendly"):
        actions.extend([
            f"{npc.key} hums softly to themselves.",
            f"{npc.key} gives you a friendly nod.",
        ])
    
    if personality.get("dutiful"):
        actions.extend([
            f"{npc.key} stands at attention.",
            f"{npc.key} scans the area alertly.",
        ])
    
    return random.choice(actions)


def npc_react_to(npc, event, character=None):
    """
    Generate an NPC reaction to an event.
    
    Args:
        npc: The NPC
        event: Event type string
        character: Character involved (if any)
    
    Returns:
        str: Reaction message or None
    """
    npc_data = get_npc_data(npc)
    personality = npc_data.get("personality", {})
    
    if event == "character_enters":
        if personality.get("dominant"):
            return f"{npc.key}'s attention shifts to the newcomer, appraising."
        elif personality.get("friendly"):
            return f"{npc.key} looks up with a welcoming smile."
        else:
            return f"{npc.key} glances toward the entrance."
    
    if event == "character_kneels":
        if personality.get("dominant"):
            if character:
                return f"{npc.key}'s eyes find {character.key}, a hint of approval in their expression."
            return f"{npc.key} notices the gesture, expression unreadable."
    
    return None


# =============================================================================
# Schedule System
# =============================================================================

def get_scheduled_location(npc, time_of_day="afternoon"):
    """
    Get where an NPC should be based on schedule.
    
    Args:
        npc: The NPC
        time_of_day: morning, afternoon, evening, night
    
    Returns:
        str: Location name or None
    """
    npc_data = get_npc_data(npc)
    schedule = npc_data.get("schedule")
    
    if not schedule:
        return npc_data.get("home_location")
    
    return schedule.get(time_of_day, npc_data.get("home_location"))


def move_npc_to_schedule(npc, time_of_day="afternoon"):
    """
    Move an NPC to their scheduled location.
    
    Args:
        npc: The NPC
        time_of_day: Current time period
    
    Returns:
        bool: If move happened
    """
    location_name = get_scheduled_location(npc, time_of_day)
    if not location_name:
        return False
    
    # Find the location
    results = search_object(location_name)
    if not results:
        return False
    
    destination = results[0]
    
    # Don't move if already there
    if npc.location == destination:
        return False
    
    # Move NPC
    old_location = npc.location
    npc.move_to(destination, quiet=True)
    
    # Announce departure/arrival
    if old_location:
        old_location.msg_contents(f"{npc.key} departs.", exclude=[npc])
    destination.msg_contents(f"{npc.key} arrives.", exclude=[npc])
    
    return True
