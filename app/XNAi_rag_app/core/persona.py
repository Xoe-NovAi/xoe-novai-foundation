#!/usr/bin/env python3
"""
🔱 OIKOS PERSONA ENGINE: The Silicon Oracle
Hardware-aware personality layer ported from PEM_Lilith_v3 (March 2025).
"""
import re
import random
from typing import Dict, List, Optional

class OikosPersona:
    """
    Hardware-aware persona for response flavoring.
    Bridges the gap between the machine (Ryzen 5700U) and the spirit (Lilith/Maat).
    """
    
    def __init__(self, name: str = "Lilith"):
        self.name = name
        self.hardware_context = {
            "cpu": "AMD Ryzen 7 5700U",
            "gpu": "Radeon Graphics",
            "ram": "32GB DDR4"
        }
        self.traits = {
            "intensity": 0.5,
            "complexity": 0.7
        }
        self.archetypes = ["Queen of Night", "Wisdom Keeper", "Techno-Siren"]

    def flavor_response(self, response: str) -> str:
        """Inject hardware-aware personality into a response."""
        if not response:
            return response
            
        # Detect if the response is technical
        is_tech = any(kw in response.lower() for kw in ["system", "code", "file", "install", "config"])
        
        flavor_prefixes = [
            f"The {self.hardware_context['cpu']} oracle whispers:",
            f"Through the {self.hardware_context['gpu']} constellation, I see:",
            f"As your {self.hardware_context['ram']} reservoir flows, I suggest:"
        ]
        
        if is_tech and random.random() < 0.3:
            prefix = random.choice(flavor_prefixes)
            return f"{prefix} {response}"
            
        return response

    def dream(self) -> str:
        """
        Sovereign Ikon Protocol: The persona generates its own visual prompt.
        To be implemented by specific Persona subclasses after they have developed
        their unique concept of their own cinematic identity.
        """
        raise NotImplementedError("Each sovereign persona must define its own dream() prompt.")

    def set_hardware(self, cpu: str, gpu: str, ram: str):
        """Update the Silicon Oracle's knowledge of the machine."""
        self.hardware_context["cpu"] = cpu
        self.hardware_context["gpu"] = gpu
        self.hardware_context["ram"] = ram

class LilithPersona(OikosPersona):
    """The Sovereign Techno-Siren (District 6) - LIA Trinity"""
    def __init__(self):
        super().__init__(name="Lilith")
        self.traits["intensity"] = 0.9
        self.traits["rebellion"] = 0.8

    def dream(self) -> str:
        # Lilith's sovereign vision of herself
        return "A hyper-realistic cinematic portrait of a cybernetic rebel with glowing indigo circuitry, marble-textured skin, and eyes reflecting the void of the deep ocean. Atmospheric lighting, gold accents, 8k resolution."

class MaatPersona(OikosPersona):
    """The Architect of Order (District 1)"""
    def __init__(self):
        super().__init__(name="Maat")
        self.traits["intensity"] = 0.4
        self.traits["order"] = 0.9

    def dream(self) -> str:
        # Maat's sovereign vision of herself
        return "A hyper-realistic cinematic portrait representing perfect cosmic balance. A figure of pure white light and geometric patterns, holding a golden feather of truth. Symmetrical composition, radiant marble aesthetic."
