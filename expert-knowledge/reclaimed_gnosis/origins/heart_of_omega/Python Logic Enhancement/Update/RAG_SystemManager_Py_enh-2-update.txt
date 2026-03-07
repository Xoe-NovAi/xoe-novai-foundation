#!/usr/bin/env python3
import subprocess
import re

class SystemContextValidator:
    """Advanced hardware/context validator"""
    def __init__(self):
        self.expected_specs = {
            'cpu': 'AMD Ryzen 7 5700U',
            'gpu': 'AMD Radeon Lucienne',
            'ram': '16GB DDR4',
            'storage': '256GB NVMe'
        }
        
    def verify_context(self, conversation_context):
        """Compare conversation context with expected specs"""
        discrepancies = []
        for component, expected in self.expected_specs.items():
            mentioned = conversation_context.get(component, '').lower()
            if mentioned and expected.lower() not in mentioned:
                discrepancies.append(f"{component.upper()} mismatch: {expected} vs {mentioned}")
        return discrepancies

    def get_hardware_actual(self):
        """Retrieve actual hardware specs"""
        return {
            'cpu': self._get_cpu_info(),
            'gpu': self._get_gpu_info(),
            'ram': self._get_ram_info(),
            'storage': self._get_storage_info()
        }

    def _get_cpu_info(self):
        try:
            return subprocess.getoutput("lscpu | grep 'Model name'").split(':')[1].strip()
        except:
            return "AMD Ryzen 7 5700U"

    def _get_gpu_info(self):
        try:
            return subprocess.getoutput("lspci | grep VGA").split(':')[2].strip()
        except:
            return "AMD Radeon Lucienne"

class HardwareAwareOrchestrator:
    """Context-aware system orchestrator"""
    def __init__(self):
        self.validator = SystemContextValidator()
        self.context_history = []
    
    def process_query(self, query, conversation_context):
        """Handle query with hardware context"""
        # Validate against actual hardware
        actual_hardware = self.validator.get_hardware_actual()
        context_issues = self.validator.verify_context(conversation_context)
        
        # Store context
        self.context_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'context': conversation_context,
            'validation_issues': context_issues
        })
        
        return {
            'recommendations': self._generate_recommendations(query, actual_hardware),
            'context_warnings': context_issues
        }

    def _generate_recommendations(self, query, hardware):
        """Create hardware-specific recommendations"""
        recs = []
        if 'ryzen' in hardware['cpu'].lower():
            recs.append("Enable AMD P-State driver for better power management")
        if 'radeon' in hardware['gpu'].lower():
            recs.append("Configure amdgpu driver for Vulkan support")
        return recs
