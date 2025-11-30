"""
Character Mixins
================

Mixins to add to Character class for various systems:
- FeralMixin: Knotting, leashing, dragging integration
- FurnitureMixin: Furniture attachment
- ItemMixin: Worn/equipped item tracking
- StatusMixin: Full status display
"""

from typing import Dict, List, Optional, Tuple
from evennia import AttributeProperty


# =============================================================================
# LEASHING MIXIN
# =============================================================================

class LeashingMixin:
    """
    Adds leash tracking for characters.
    
    Attributes:
        leash_data: Dict with leash state
        holding_leash: dbref of leash being held
    """
    
    leash_data = AttributeProperty(default=None)
    holding_leash = AttributeProperty(default=None)
    
    def is_leashed(self) -> bool:
        """Check if currently leashed."""
        return bool(self.leash_data)
    
    def is_holding_leash(self) -> bool:
        """Check if holding a leash."""
        return bool(self.holding_leash)
    
    def get_leash_holder(self):
        """Get who's holding our leash."""
        if not self.leash_data:
            return None
        
        holder_dbref = self.leash_data.get("holder")
        if holder_dbref:
            try:
                from evennia.utils.search import search_object
                results = search_object(holder_dbref)
                return results[0] if results else None
            except Exception:
                pass
        return None
    
    def get_leashed_creature(self):
        """Get creature on leash we're holding."""
        if not self.holding_leash:
            return None
        
        try:
            from evennia.utils.search import search_object
            leash_results = search_object(self.holding_leash)
            if leash_results:
                leash = leash_results[0]
                if hasattr(leash, 'get_leashed_creature'):
                    return leash.get_leashed_creature()
        except Exception:
            pass
        return None
    
    def get_leash_status(self) -> str:
        """Get formatted leash status."""
        if self.is_leashed():
            holder = self.get_leash_holder()
            holder_name = holder.key if holder else "someone"
            return f"Leashed to {holder_name}"
        
        if self.is_holding_leash():
            creature = self.get_leashed_creature()
            creature_name = creature.key if creature else "something"
            return f"Holding {creature_name}'s leash"
        
        return ""


# =============================================================================
# KNOTTING MIXIN
# =============================================================================

class KnottingMixin:
    """
    Adds knot tie tracking for characters.
    
    Attributes:
        tie_data: Dict with current tie state
    """
    
    tie_data = AttributeProperty(default=None)
    
    def is_tied(self) -> bool:
        """Check if currently knotted/tied."""
        return bool(self.tie_data)
    
    def get_tied_partner(self):
        """Get partner we're tied with."""
        if not self.tie_data:
            return None
        
        partner_dbref = self.tie_data.get("partner")
        if partner_dbref:
            try:
                from evennia.utils.search import search_object
                results = search_object(partner_dbref)
                return results[0] if results else None
            except Exception:
                pass
        return None
    
    def get_tie_role(self) -> str:
        """Get role in current tie (penetrator/receiver)."""
        if not self.tie_data:
            return ""
        return self.tie_data.get("role", "")
    
    def get_knot_state(self) -> str:
        """Get current knot state."""
        if not self.tie_data:
            return ""
        return self.tie_data.get("knot_state", "")
    
    def get_knot_status(self) -> str:
        """Get formatted knot status."""
        if not self.is_tied():
            return ""
        
        partner = self.get_tied_partner()
        partner_name = partner.key if partner else "someone"
        role = self.get_tie_role()
        state = self.get_knot_state()
        
        if role == "penetrator":
            return f"Knotted inside {partner_name} ({state})"
        else:
            return f"Knotted by {partner_name} ({state})"


# =============================================================================
# DRAGGING MIXIN
# =============================================================================

class DraggingMixin:
    """
    Adds drag mechanics - being dragged or dragging others.
    """
    
    being_dragged_by = AttributeProperty(default=None)
    dragging = AttributeProperty(default=None)
    
    def is_being_dragged(self) -> bool:
        return bool(self.being_dragged_by)
    
    def is_dragging(self) -> bool:
        return bool(self.dragging)
    
    def get_dragger(self):
        """Get who's dragging us."""
        if not self.being_dragged_by:
            return None
        try:
            from evennia.utils.search import search_object
            results = search_object(self.being_dragged_by)
            return results[0] if results else None
        except Exception:
            return None
    
    def get_dragged(self):
        """Get who we're dragging."""
        if not self.dragging:
            return None
        try:
            from evennia.utils.search import search_object
            results = search_object(self.dragging)
            return results[0] if results else None
        except Exception:
            return None


# =============================================================================
# FERAL MIXIN (Combined)
# =============================================================================

class FeralMixin(KnottingMixin, LeashingMixin, DraggingMixin):
    """
    Combined mixin for feral mechanics.
    
    Handles movement restrictions from:
    - Being leashed
    - Being knotted
    - Being dragged
    
    And dragging others when moving while:
    - Holding a leash
    - Being the penetrator in a knot
    """
    
    def at_pre_move(self, destination, **kwargs):
        """Check if movement is allowed."""
        # Leash check
        if self.is_leashed():
            holder = self.get_leash_holder()
            if holder and holder.location == self.location:
                # Holder is here, can't just walk away
                if not kwargs.get("forced"):
                    self.msg("The leash holds you back.")
                    return False
        
        # Knot check (receiver can't move)
        if self.is_tied() and self.get_tie_role() == "receiver":
            if not kwargs.get("forced"):
                self.msg("You're knotted and can't move!")
                return False
        
        return True
    
    def at_post_move(self, source_location, **kwargs):
        """Handle dragging after movement."""
        # Drag leashed creature
        if self.is_holding_leash():
            creature = self.get_leashed_creature()
            if creature and creature.location == source_location:
                creature.msg(f"{self.key} tugs you along by the leash.")
                creature.move_to(self.location, quiet=True, forced=True)
                self.location.msg_contents(
                    f"{self.key} leads {creature.key} in on a leash.",
                    exclude=[self, creature]
                )
        
        # Drag knotted partner
        if self.is_tied() and self.get_tie_role() == "penetrator":
            partner = self.get_tied_partner()
            if partner and partner.location == source_location:
                partner.msg(f"{self.key} drags you along, still knotted together!")
                partner.move_to(self.location, quiet=True, forced=True)
                self.location.msg_contents(
                    f"{self.key} enters, dragging {partner.key} along - "
                    "they appear to be stuck together.",
                    exclude=[self, partner]
                )


# =============================================================================
# FURNITURE MIXIN
# =============================================================================

class FurnitureMixin:
    """
    Adds furniture attachment tracking.
    
    Attributes:
        using_furniture_dbref: dbref of furniture being used
        furniture_slot: which slot on the furniture
        furniture_locked: if locked to furniture
    """
    
    using_furniture_dbref = AttributeProperty(default=None)
    furniture_slot = AttributeProperty(default=None)
    furniture_locked = AttributeProperty(default=False)
    
    def get_furniture(self):
        """Get furniture object currently using."""
        if not self.using_furniture_dbref:
            return None
        try:
            from evennia.utils.search import search_object
            results = search_object(self.using_furniture_dbref)
            return results[0] if results else None
        except Exception:
            return None
    
    def is_on_furniture(self) -> bool:
        """Check if currently on furniture."""
        return bool(self.using_furniture_dbref)
    
    def is_restrained_by_furniture(self) -> bool:
        """Check if restrained by furniture."""
        return self.furniture_locked
    
    def attach_to_furniture(self, furniture, slot: str = None) -> Tuple[bool, str]:
        """Attach to furniture."""
        if self.using_furniture_dbref:
            return False, "Already using furniture."
        
        if hasattr(furniture, 'add_occupant'):
            success, msg = furniture.add_occupant(self, slot)
            if success:
                self.using_furniture_dbref = furniture.dbref
                self.furniture_slot = slot
            return success, msg
        
        self.using_furniture_dbref = furniture.dbref
        self.furniture_slot = slot
        return True, f"You use the {furniture.key}."
    
    def detach_from_furniture(self, force: bool = False) -> Tuple[bool, str]:
        """Detach from furniture."""
        if not self.using_furniture_dbref:
            return False, "Not using any furniture."
        
        if self.furniture_locked and not force:
            return False, "You're locked to the furniture!"
        
        furniture = self.get_furniture()
        if furniture and hasattr(furniture, 'remove_occupant'):
            furniture.remove_occupant(self)
        
        self.using_furniture_dbref = None
        self.furniture_slot = None
        self.furniture_locked = False
        
        return True, "You get off the furniture."
    
    def get_furniture_status(self) -> str:
        """Get formatted furniture status."""
        if not self.is_on_furniture():
            return ""
        
        furniture = self.get_furniture()
        name = furniture.key if furniture else "furniture"
        
        if self.furniture_locked:
            return f"Restrained on {name}"
        return f"Using {name}"


# =============================================================================
# ITEM MIXIN
# =============================================================================

class ItemMixin:
    """
    Adds worn/equipped item tracking.
    """
    
    def get_worn_items(self) -> List:
        """Get all worn items."""
        worn = []
        for obj in self.contents:
            if hasattr(obj, 'worn_by') and obj.worn_by == self.dbref:
                worn.append(obj)
        return worn
    
    def get_worn_at(self, location: str):
        """Get item worn at a specific location."""
        for obj in self.contents:
            if hasattr(obj, 'worn_by') and obj.worn_by == self.dbref:
                wear_loc = getattr(obj, 'wear_location', None)
                if wear_loc:
                    loc_val = wear_loc.value if hasattr(wear_loc, 'value') else wear_loc
                    if loc_val == location:
                        return obj
        return None
    
    def is_collared(self) -> bool:
        """Check if wearing a collar."""
        return self.get_worn_at("neck") is not None
    
    def is_gagged(self) -> bool:
        """Check if gagged."""
        return self.get_worn_at("mouth") is not None
    
    def is_blindfolded(self) -> bool:
        """Check if blindfolded."""
        return self.get_worn_at("eyes") is not None
    
    def is_restrained(self) -> bool:
        """Check if wearing any restraints."""
        for obj in self.get_worn_items():
            item_type = getattr(obj, 'item_type', None)
            if item_type:
                type_val = item_type.value if hasattr(item_type, 'value') else item_type
                if type_val == "restraint":
                    return True
        return False
    
    def get_collar(self):
        """Get collar if wearing one."""
        return self.get_worn_at("neck")
    
    def filter_speech(self, text: str) -> str:
        """Filter speech through any gag."""
        gag = self.get_worn_at("mouth")
        if gag and hasattr(gag, 'filter_speech'):
            return gag.filter_speech(text)
        return text


# =============================================================================
# STATUS MIXIN
# =============================================================================

class StatusMixin:
    """
    Adds full status display combining all systems.
    """
    
    def get_full_status(self) -> str:
        """Get complete status string."""
        lines = []
        
        # Position (if set)
        position = getattr(self, 'position', '')
        if position:
            lines.append(f"Position: {position}")
        
        # Furniture
        if hasattr(self, 'get_furniture_status'):
            furn_status = self.get_furniture_status()
            if furn_status:
                lines.append(f"Furniture: {furn_status}")
        
        # Knot
        if hasattr(self, 'get_knot_status'):
            knot_status = self.get_knot_status()
            if knot_status:
                lines.append(f"Tied: {knot_status}")
        
        # Leash
        if hasattr(self, 'get_leash_status'):
            leash_status = self.get_leash_status()
            if leash_status:
                lines.append(f"Leash: {leash_status}")
        
        # Worn items
        if hasattr(self, 'get_worn_items'):
            worn = self.get_worn_items()
            if worn:
                item_names = [obj.key for obj in worn]
                lines.append(f"Wearing: {', '.join(item_names)}")
        
        # Arousal
        if hasattr(self, 'get_arousal_level'):
            arousal = self.get_arousal_level()
            if arousal and arousal != "calm":
                lines.append(f"Arousal: {arousal}")
        
        # Restraints
        if hasattr(self, 'is_restrained') and self.is_restrained():
            lines.append("Status: Restrained")
        
        if hasattr(self, 'is_gagged') and self.is_gagged():
            lines.append("Status: Gagged")
        
        if hasattr(self, 'is_blindfolded') and self.is_blindfolded():
            lines.append("Status: Blindfolded")
        
        return "\n".join(lines) if lines else "No notable status."


# =============================================================================
# COMBINED CHARACTER MIXINS
# =============================================================================

class CharacterMixins(FeralMixin, FurnitureMixin, ItemMixin, StatusMixin):
    """
    All character mixins combined.
    
    Add to Character class:
        class Character(CharacterMixins, ObjectParent, DefaultCharacter):
            ...
    """
    pass


__all__ = [
    "LeashingMixin", "KnottingMixin", "DraggingMixin", "FeralMixin",
    "FurnitureMixin", "ItemMixin", "StatusMixin", "CharacterMixins",
]
