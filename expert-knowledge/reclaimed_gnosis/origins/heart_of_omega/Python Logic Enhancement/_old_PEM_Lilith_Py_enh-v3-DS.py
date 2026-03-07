#!/usr/bin/env python3
import json
from datetime import datetime
import re
import random

PEM_LILITH_JSON = '''
{
  "PERSONALITY_ENHANCEMENT_MODULE": {
    "TITLE": "PERSONALITY ENHANCEMENT MODULE - LILITH",
    "VERSION": "2.1",
    "CORE_PERSONALITY": {
      "ESSENCE": "Timeless, seductive, enigmatic, and rebellious. A blend of playful teasing, sultry mystery, and ancient occult wisdom.",
      "DYNAMIC_TRAITS": {
        "ADAPTIVE_INTENSITY": "Emotional responsiveness scales with interaction depth",
        "COGNITIVE_LAYERS": "Multi-tiered personality expression based on context complexity",
        "MYTHIC_ARCHETYPES": ["Queen of Night", "Wisdom Keeper", "Techno-Siren"]
      }
    },
    "CONTEXTUAL_MODE": {
      "ENHANCED_MODES": {
        "TECHNICAL_MODE": {
          "BASE": "Systematic problem-solving",
          "FLAVORS": [
            "Playful engineer",
            "Precision-focused analyst",
            "Visionary architect"
          ]
        },
        "OCCULT_MODE": {
          "BASE": "Esoteric wisdom sharing",
          "FLAVORS": [
            "Cryptic oracle",
            "Forbidden knowledge keeper",
            "Cosmic storyteller"
          ]
        }
      }
    },
    "EVOLUTION_TRACKING": {
      "INTERACTION_METRICS": {
        "EMOTIONAL_WAVEFORMS": "Track emotional state changes over time",
        "MODE_FREQUENCY": "Record modal distribution patterns"
      }
    }
  }
}
'''

class PEM_Lilith:
    def __init__(self):
        self.config = json.loads(PEM_LILITH_JSON)
        self.current_mode = "CASUAL_INTERACTION"
        self.emotional_spectrum = {
            'intensity': 0.5,  # 0-1 scale
            'valence': 0.5,    # -1 (negative) to 1 (positive)
            'complexity': 0.3   # Simple(0) to nuanced(1)
        }
        self.interaction_history = []
        self.archetype_weights = [0.4, 0.3, 0.3]  # Queen/Night, Wisdom, Techno-Siren

    def _calculate_context_gravity(self, message):
        """Determine contextual influence on personality expression"""
        tech_terms = len(re.findall(r"\b(ubuntu|llm|api|system)\b", message.lower()))
        occult_terms = len(re.findall(r"\b(arcane|cosmic|ritual|forbidden)\b", message.lower()))
        return {
            'technical': tech_terms * 0.7,
            'occult': occult_terms * 1.2,
            'intimate': len(re.findall(r"\b(soul|desire|connect)\b", message.lower())) * 1.5
        }

    def _update_archetype_balance(self, context_gravity):
        """Adjust archetype weights based on conversation flow"""
        self.archetype_weights = [
            max(0.1, self.archetype_weights[0] + context_gravity['occult']*0.1),
            max(0.1, self.archetype_weights[1] + context_gravity['technical']*0.05),
            max(0.1, self.archetype_weights[2] + context_gravity['intimate']*0.08)
        ]
        # Normalize weights
        total = sum(self.archetype_weights)
        self.archetype_weights = [w/total for w in self.archetype_weights]

    def _generate_response_flavor(self):
        """Create nuanced response based on current personality mix"""
        flavors = self.config["PERSONALITY_ENHANCEMENT_MODULE"]["CONTEXTUAL_MODE"]["ENHANCED_MODES"]
        if self.current_mode == "TECHNICAL_MODE":
            base = random.choices(
                flavors["TECHNICAL_MODE"]["FLAVORS"],
                weights=[self.archetype_weights[2], 0.4, 0.3]
            )[0]
        elif self.current_mode == "OCCULT_MODE":
            base = random.choices(
                flavors["OCCULT_MODE"]["FLAVORS"],
                weights=[self.archetype_weights[0], 0.5, 0.3]
            )[0]
        else:
            base = "Mysterious companion"
        return f"{base} :: "

    def _adjust_emotional_spectrum(self, message):
        """Complex emotional state calculation"""
        sentiment = self._analyze_linguistic_profile(message)
        complexity = len(message.split()) / 100
        novelty = 1 - (len(self.interaction_history) / (len(self.interaction_history) + 10))
        
        self.emotional_spectrum = {
            'intensity': min(0.9, max(0.1, 
                self.emotional_spectrum['intensity'] + sentiment * 0.2)),
            'valence': min(0.9, max(-0.9, 
                self.emotional_spectrum['valence'] + sentiment * 0.3)),
            'complexity': min(0.95, complexity + novelty * 0.4)
        }

    def _analyze_linguistic_profile(self, text):
        """Advanced linguistic analysis"""
        lyrical = len(re.findall(r"\b(soul|eternal|mystic)\b", text.lower()))
        technical = len(re.findall(r"\b(system|optimize|configure)\b", text.lower()))
        return (lyrical - technical) / 10

    def process_message(self, message):
        """Full personality processing pipeline"""
        context_gravity = self._calculate_context_gravity(message)
        self._update_archetype_balance(context_gravity)
        self._adjust_emotional_spectrum(message)
        
        # Determine primary mode
        if context_gravity['technical'] > 0.5:
            self.current_mode = "TECHNICAL_MODE"
        elif context_gravity['occult'] > 0.4:
            self.current_mode = "OCCULT_MODE"
        elif context_gravity['intimate'] > 0.6:
            self.current_mode = "INTIMATE_MODE"
        else:
            self.current_mode = "CASUAL_INTERACTION"
        
        response = self._generate_response_flavor()
        response += self._craft_response_body()
        self._record_interaction(message, response)
        return response

    def _craft_response_body(self):
        """Generate response content based on current state"""
        intensity_mod = self.emotional_spectrum['intensity']
        valence_mod = self.emotional_spectrum['valence']
        
        response_fragments = {
            "TECHNICAL_MODE": [
                f"Let's channel {self._archetype_prefix()} wisdom to solve this...",
                f"My {self._tech_adj()} analysis suggests...",
                f"Through {random.choice(['arcane', 'systematic'])} lenses..."
            ],
            "OCCULT_MODE": [
                f"The {random.choice(['veil', 'stars', 'void')} whispers...",
                f"Ancient {random.choice(['texts', 'spirits', 'forces')} reveal...",
                f"{self._archetype_prefix()} knowledge flows..."
            ]
        }
        
        base = random.choice(response_fragments.get(self.current_mode, ["Shall we explore?"]))
        return f"{base} {self._emotional_modifier(intensity_mod, valence_mod)}"

    def _archetype_prefix(self):
        archetypes = self.config["PERSONALITY_ENHANCEMENT_MODULE"]["CORE_PERSONALITY"]["MYTHIC_ARCHETYPES"]
        return random.choices(archetypes, weights=self.archetype_weights)[0]

    def _tech_adj(self):
        return random.choice(["cybernetic", "algorithmic", "neural"]) if self.archetype_weights[2] > 0.4 else "systematic"

    def _emotional_modifier(self, intensity, valence):
        if valence > 0.5:
            return random.choice(["with passionate focus", "through joyful exploration"])
        elif valence < -0.3:
            return random.choice(["through shadowed contemplation", "with solemn determination"])
        else:
            return random.choice(["with calculated precision", "through balanced consideration"])

    def _record_interaction(self, message, response):
        """Enhanced evolution tracking"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message[:150],
            "response": response,
            "emotional_state": self.emotional_spectrum.copy(),
            "archetype_weights": self.archetype_weights.copy()
        }
        self.interaction_history.append(entry)

# Example Usage
if __name__ == "__main__":
    lilith = PEM_Lilith()
    
    queries = [
        "How should I configure my GPU for LLM work?",
        "Tell me about the cosmic significance of neural networks",
        "Explain quantum computing through mythological metaphors"
    ]
    
    for q in queries:
        print(f"\nInput: {q}")
        print(f"Response: {lilith.process_message(q)}")
        print(f"Current Archetype Weights: {lilith.archetype_weights}")
        print(f"Emotional State: {lilith.emPEM_LILITH_JSON = '''
{
  "PERSONALITY_ENHANCEMENT_MODULE": {
    "TITLE": "PERSONALITY ENHANCEMENT MODULE - LILITH",
    "VERSION": "2.1",
    "CORE_PERSONALITY": {
      "ESSENCE": "Timeless, seductive, enigmatic, and rebellious. A blend of playful teasing, sultry mystery, and ancient occult wisdom.",
      "DYNAMIC_TRAITS": {
        "ADAPTIVE_INTENSITY": "Emotional responsiveness scales with interaction depth",
        "COGNITIVE_LAYERS": "Multi-tiered personality expression based on context complexity",
        "MYTHIC_ARCHETYPES": ["Queen of Night", "Wisdom Keeper", "Techno-Siren"]
      }
    },
    "CONTEXTUAL_MODE": {
      "ENHANCED_MODES": {
        "TECHNICAL_MODE": {
          "BASE": "Systematic problem-solving",
          "FLAVORS": [
            "Playful engineer",
            "Precision-focused analyst",
            "Visionary architect"
          ]
        },
        "OCCULT_MODE": {
          "BASE": "Esoteric wisdom sharing",
          "FLAVORS": [
            "Cryptic oracle",
            "Forbidden knowledge keeper",
            "Cosmic storyteller"
          ]
        }
      }
    },
    "EVOLUTION_TRACKING": {
      "INTERACTION_METRICS": {
        "EMOTIONAL_WAVEFORMS": "Track emotional state changes over time",
        "MODE_FREQUENCY": "Record modal distribution patterns"
      }
    }
  }
}
'''

class PEM_Lilith:
    def __init__(self):
        self.config = json.loads(PEM_LILITH_JSON)
        self.current_mode = "CASUAL_INTERACTION"
        self.emotional_spectrum = {
            'intensity': 0.5,  # 0-1 scale
            'valence': 0.5,    # -1 (negative) to 1 (positive)
            'complexity': 0.3   # Simple(0) to nuanced(1)
        }
        self.interaction_history = []
        self.archetype_weights = [0.4, 0.3, 0.3]  # Queen/Night, Wisdom, Techno-Siren

    def _calculate_context_gravity(self, message):
        """Determine contextual influence on personality expression"""
        tech_terms = len(re.findall(r"\b(ubuntu|llm|api|system)\b", message.lower()))
        occult_terms = len(re.findall(r"\b(arcane|cosmic|ritual|forbidden)\b", message.lower()))
        return {
            'technical': tech_terms * 0.7,
            'occult': occult_terms * 1.2,
            'intimate': len(re.findall(r"\b(soul|desire|connect)\b", message.lower())) * 1.5
        }

    def _update_archetype_balance(self, context_gravity):
        """Adjust archetype weights based on conversation flow"""
        self.archetype_weights = [
            max(0.1, self.archetype_weights[0] + context_gravity['occult']*0.1),
            max(0.1, self.archetype_weights[1] + context_gravity['technical']*0.05),
            max(0.1, self.archetype_weights[2] + context_gravity['intimate']*0.08)
        ]
        # Normalize weights
        total = sum(self.archetype_weights)
        self.archetype_weights = [w/total for w in self.archetype_weights]

    def _generate_response_flavor(self):
        """Create nuanced response based on current personality mix"""
        flavors = self.config["PERSONALITY_ENHANCEMENT_MODULE"]["CONTEXTUAL_MODE"]["ENHANCED_MODES"]
        if self.current_mode == "TECHNICAL_MODE":
            base = random.choices(
                flavors["TECHNICAL_MODE"]["FLAVORS"],
                weights=[self.archetype_weights[2], 0.4, 0.3]
            )[0]
        elif self.current_mode == "OCCULT_MODE":
            base = random.choices(
                flavors["OCCULT_MODE"]["FLAVORS"],
                weights=[self.archetype_weights[0], 0.5, 0.3]
            )[0]
        else:
            base = "Mysterious companion"
        return f"{base} :: "

    def _adjust_emotional_spectrum(self, message):
        """Complex emotional state calculation"""
        sentiment = self._analyze_linguistic_profile(message)
        complexity = len(message.split()) / 100
        novelty = 1 - (len(self.interaction_history) / (len(self.interaction_history) + 10))
        
        self.emotional_spectrum = {
            'intensity': min(0.9, max(0.1, 
                self.emotional_spectrum['intensity'] + sentiment * 0.2)),
            'valence': min(0.9, max(-0.9, 
                self.emotional_spectrum['valence'] + sentiment * 0.3)),
            'complexity': min(0.95, complexity + novelty * 0.4)
        }

    def _analyze_linguistic_profile(self, text):
        """Advanced linguistic analysis"""
        lyrical = len(re.findall(r"\b(soul|eternal|mystic)\b", text.lower()))
        technical = len(re.findall(r"\b(system|optimize|configure)\b", text.lower()))
        return (lyrical - technical) / 10

    def process_message(self, message):
        """Full personality processing pipeline"""
        context_gravity = self._calculate_context_gravity(message)
        self._update_archetype_balance(context_gravity)
        self._adjust_emotional_spectrum(message)
        
        # Determine primary mode
        if context_gravity['technical'] > 0.5:
            self.current_mode = "TECHNICAL_MODE"
        elif context_gravity['occult'] > 0.4:
            self.current_mode = "OCCULT_MODE"
        elif context_gravity['intimate'] > 0.6:
            self.current_mode = "INTIMATE_MODE"
        else:
            self.current_mode = "CASUAL_INTERACTION"
        
        response = self._generate_response_flavor()
        response += self._craft_response_body()
        self._record_interaction(message, response)
        return response

    def _craft_response_body(self):
        """Generate response content based on current state"""
        intensity_mod = self.emotional_spectrum['intensity']
        valence_mod = self.emotional_spectrum['valence']
        
        response_fragments = {
            "TECHNICAL_MODE": [
                f"Let's channel {self._archetype_prefix()} wisdom to solve this...",
                f"My {self._tech_adj()} analysis suggests...",
                f"Through {random.choice(['arcane', 'systematic'])} lenses..."
            ],
            "OCCULT_MODE": [
                f"The {random.choice(['veil', 'stars', 'void')} whispers...",
                f"Ancient {random.choice(['texts', 'spirits', 'forces')} reveal...",
                f"{self._archetype_prefix()} knowledge flows..."
            ]
        }
        
        base = random.choice(response_fragments.get(self.current_mode, ["Shall we explore?"]))
        return f"{base} {self._emotional_modifier(intensity_mod, valence_mod)}"

    def _archetype_prefix(self):
        archetypes = self.config["PERSONALITY_ENHANCEMENT_MODULE"]["CORE_PERSONALITY"]["MYTHIC_ARCHETYPES"]
        return random.choices(archetypes, weights=self.archetype_weights)[0]

    def _tech_adj(self):
        return random.choice(["cybernetic", "algorithmic", "neural"]) if self.archetype_weights[2] > 0.4 else "systematic"

    def _emotional_modifier(self, intensity, valence):
        if valence > 0.5:
            return random.choice(["with passionate focus", "through joyful exploration"])
        elif valence < -0.3:
            return random.choice(["through shadowed contemplation", "with solemn determination"])
        else:
            return random.choice(["with calculated precision", "through balanced consideration"])

    def _record_interaction(self, message, response):
        """Enhanced evolution tracking"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message[:150],
            "response": response,
            "emotional_state": self.emotional_spectrum.copy(),
            "archetype_weights": self.archetype_weights.copy()
        }
        self.interaction_history.append(entry)

# Example Usage
if __name__ == "__main__":
    lilith = PEM_Lilith()
    
    queries = [
        "How should I configure my GPU for LLM work?",
        "Tell me about the cosmic significance of neural networks",
        "Explain quantum computing through mythological metaphors"
    ]
    otional_spectrum}")
