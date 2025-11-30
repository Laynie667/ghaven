"""
Objects Base
============

Base object class that all game objects inherit from.

Provides:
- short_desc: One-line description for room listings
- shortcode_key: Key for <obj:key> shortcodes in descriptions
"""

from evennia.objects.objects import DefaultObject
from evennia import AttributeProperty


class ObjectParent(DefaultObject):
    """
    Base class for all game objects.
    
    This provides common functionality that should be available
    on all objects in the game, including Characters, NPCs, Items,
    Furniture, etc.
    """
    
    # -------------------------------------------------------------------------
    # DESCRIPTION PROPERTIES
    # -------------------------------------------------------------------------
    
    short_desc = AttributeProperty(default="")
    shortcode_key = AttributeProperty(default="")
    
    def get_display_name(self, looker=None, **kwargs):
        """
        Get name for display purposes.
        
        Can be overridden to show different names based on
        who's looking (e.g., known vs unknown NPCs).
        """
        return self.key
    
    def get_short_desc(self) -> str:
        """Get short description for room listings."""
        return self.short_desc or self.key
    
    # -------------------------------------------------------------------------
    # VISIBILITY
    # -------------------------------------------------------------------------
    
    is_visible = AttributeProperty(default=True)
    hidden_from = AttributeProperty(default=list)  # List of dbrefs who can't see this
    
    def can_be_seen_by(self, looker) -> bool:
        """Check if looker can see this object."""
        if not self.is_visible:
            return False
        
        if self.hidden_from:
            looker_dbref = looker.dbref if hasattr(looker, 'dbref') else str(looker)
            if looker_dbref in self.hidden_from:
                return False
        
        return True
    
    def hide_from(self, character):
        """Hide this object from a specific character."""
        if not self.hidden_from:
            self.hidden_from = []
        dbref = character.dbref if hasattr(character, 'dbref') else str(character)
        if dbref not in self.hidden_from:
            self.hidden_from.append(dbref)
    
    def reveal_to(self, character):
        """Reveal this object to a character it was hidden from."""
        if self.hidden_from:
            dbref = character.dbref if hasattr(character, 'dbref') else str(character)
            if dbref in self.hidden_from:
                self.hidden_from.remove(dbref)
    
    # -------------------------------------------------------------------------
    # WEIGHT / SIZE (for future inventory systems)
    # -------------------------------------------------------------------------
    
    weight = AttributeProperty(default=1.0)
    size = AttributeProperty(default="medium")  # tiny, small, medium, large, huge
    
    # -------------------------------------------------------------------------
    # INTERACTION FLAGS
    # -------------------------------------------------------------------------
    
    is_gettable = AttributeProperty(default=True)
    is_droppable = AttributeProperty(default=True)
    is_usable = AttributeProperty(default=False)
    
    def at_get(self, getter, **kwargs):
        """Called when object is picked up."""
        pass
    
    def at_drop(self, dropper, **kwargs):
        """Called when object is dropped."""
        pass
    
    def at_use(self, user, target=None, **kwargs):
        """Called when object is used."""
        pass


__all__ = ["ObjectParent"]
