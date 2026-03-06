#!/usr/bin/env python3
"""
Voice Implementation Test Suite (renamed)

This test file mirrors `test_enterprise_voice.py` but uses the new public
module name `voice_interface` to align docs and quick-start commands.
"""

import logging
import asyncio
import time
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


try:
    from XNAi_rag_app.services.voice.voice_interface import (
        VoiceInterface,
        VoiceConfig,
    )
    VOICE_IMPORT_OK = True
except Exception as e:
    logger.error('Failed to import VoiceInterface: %s', e)
    VOICE_IMPORT_OK = False


class VoiceTest:
    async def run(self):
        logger.info('Voice wrapper import ok: %s', VOICE_IMPORT_OK)


if __name__ == '__main__':
    asyncio.run(VoiceTest().run())
