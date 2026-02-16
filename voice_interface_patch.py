import sys

with open('app/XNAi_rag_app/services/voice/voice_interface.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if 'self.stt_provider_name = "faster_whisper"' in line:
        new_lines.append(line)
        new_lines.append('        self.loaded_model_name = None\n')
        continue
    
    if 'def _initialize_models(self):' in line:
        new_lines.append(line)
        new_lines.append('        # Get current degradation tier and select appropriate model\n')
        new_lines.append('        try:\n')
        new_lines.append('            from ...core.tier_config import tier_config_factory\n')
        new_lines.append('            current_tier = tier_config_factory.get_current_tier()\n')
        new_lines.append('            selected_model_name = self._select_whisper_model(current_tier)\n')
        new_lines.append('            \n')
        new_lines.append('            # Skip if already loaded\n')
        new_lines.append('            if self.stt_model is not None and getattr(self, "loaded_model_name", None) == selected_model_name:\n')
        new_lines.append('                return\n')
        new_lines.append('            \n')
        new_lines.append('            # STT model loading with tier-aware model selection\n')
        new_lines.append('            if self.config.stt_provider == STTProvider.FASTER_WHISPER and FASTER_WHISPER_AVAILABLE:\n')
        new_lines.append('                # CLAUDE CRITICAL: Memory cleanup before reloading\n')
        new_lines.append('                if self.stt_model is not None:\n')
        new_lines.append('                    logger.info(f"Unloading model {self.loaded_model_name} to load {selected_model_name} (Tier {current_tier})...")\n')
        new_lines.append('                    del self.stt_model\n')
        new_lines.append('                    self.stt_model = None\n')
        new_lines.append('                    gc.collect()\n')
        new_lines.append('                    time.sleep(0.1)\n')
        new_lines.append('\n')
        new_lines.append('                try:\n')
        new_lines.append('                    # Check for local models in current working directory\n')
        new_lines.append('                    current_dir = Path(__file__).parent.parent.parent.parent\n')
        new_lines.append('                    local_whisper_path = current_dir / "models" / selected_model_name\n')
        new_lines.append('                    \n')
        new_lines.append('                    if self.config.offline_mode:\n')
        new_lines.append('                        if not local_whisper_path.exists():\n')
        new_lines.append('                            logger.warning(f"Offline mode: Local Whisper model not found at {local_whisper_path}. Skipping.")\n')
        new_lines.append('                            self.stt_model = None\n')
        new_lines.append('                        else:\n')
        new_lines.append('                            logger.info(f"Loading local Faster Whisper from: {local_whisper_path} (Tier {current_tier})")\n')
        new_lines.append('                            self.stt_model = WhisperModel(\n')
        new_lines.append('                                str(local_whisper_path),\n')
        new_lines.append('                                device=self.config.stt_device,\n')
        new_lines.append('                                compute_type=self.config.stt_compute_type,\n')
        new_lines.append('                            )\n')
        new_lines.append('                    else:\n')
        new_lines.append('                        model_path = str(local_whisper_path) if local_whisper_path.exists() else selected_model_name\n')
        new_lines.append('                        logger.info(f"Loading Faster Whisper from: {model_path} (Tier {current_tier})")\n')
        new_lines.append('                        self.stt_model = WhisperModel(\n')
        new_lines.append('                            model_path,\n')
        new_lines.append('                            device=self.config.stt_device,\n')
        new_lines.append('                            compute_type=self.config.stt_compute_type,\n')
        new_lines.append('                        )\n')
        new_lines.append('                    \n')
        new_lines.append('                    if self.stt_model:\n')
        new_lines.append('                        self.loaded_model_name = selected_model_name\n')
        new_lines.append('                        voice_metrics.update_model_loaded("stt", self.stt_provider_name, True)\n')
        new_lines.append('                        logger.info(f"Faster Whisper {selected_model_name} loaded successfully (Tier {current_tier})")\n')
        new_lines.append('                        \n')
        new_lines.append('                except Exception as e:\n')
        new_lines.append('                    logger.error(f"Failed to load Faster Whisper: {e}")\n')
        new_lines.append('                    voice_metrics.update_model_loaded("stt", self.stt_provider_name, False)\n')
        new_lines.append('        except Exception as e:\n')
        new_lines.append('            logger.warning(f"Failed to get degradation tier for model selection: {e}")\n')
        new_lines.append('            self._load_original_stt_model()\n')
        
        # Now we need to skip the original implementation of _initialize_models until the TTS part
        skip = True
        continue
    
    if skip and 'if self.config.tts_provider == TTSProvider.PIPER_ONNX:' in line:
        skip = False
        # Don't continue, fall through to add the TTS logic
        
    if not skip:
        new_lines.append(line)

with open('app/XNAi_rag_app/services/voice/voice_interface.py', 'w') as f:
    f.writelines(new_lines)
