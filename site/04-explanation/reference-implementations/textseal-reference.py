# ============================================================================
# INTEGRATION STATUS: CLAUDE IMPLEMENTATION DELIVERABLE
# ============================================================================
# Status: NOT INTEGRATED - Requires implementation into Xoe-NovAi codebase
# Source: Claude Week 4 Session Deliverable
# Date Received: January 27, 2026
# Implementation Priority: HIGH (Content provenance & EU AI Act compliance)
# Estimated Integration Effort: 2-3 days
# Dependencies: Cryptography libraries, C2PA manifest generation, Unicode steganography
# Integration Checklist:
# - [ ] Implement TextSealEngine class with watermarking methods
# - [ ] Deploy FastAPI service with watermark/verify endpoints
# - [ ] Integrate C2PA manifest generation and cryptographic signing
# - [ ] Implement multiple embedding techniques (homoglyphs, zero-width, whitespace)
# - [ ] Add Prometheus metrics for watermarking operations
# - [ ] Test end-to-end watermarking and verification workflows
# - [ ] Validate imperceptible watermarking quality
# Integration Complete: [ ] Date: ___________ By: ___________
# ============================================================================

# app/security/textseal_service_complete.py
"""
Xoe-NovAi Complete TextSeal Watermarking Service
C2PA-compliant cryptographic watermarking for AI-generated content
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import hashlib
import json
import uuid
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import logging
import os
from dataclasses import dataclass
import asyncio
from prometheus_client import Counter, Histogram, Gauge
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Xoe-NovAi TextSeal Service",
    description="Cryptographic Watermarking & Content Provenance",
    version="1.0.0"
)

# ============================================================================
# METRICS
# ============================================================================

watermark_embedding_duration = Histogram(
    'watermark_embedding_duration_seconds',
    'Watermark embedding latency',
    ['method']
)

watermark_verification_success = Counter(
    'watermark_verification_success_total',
    'Successful watermark verifications',
    ['method']
)

watermark_verification_failure = Counter(
    'watermark_verification_failure_total',
    'Failed watermark verifications',
    ['method', 'reason']
)

watermark_operations_total = Counter(
    'watermark_operations_total',
    'Total watermarking operations',
    ['operation']
)

# ============================================================================
# MODELS
# ============================================================================

class WatermarkRequest(BaseModel):
    content: str
    metadata: Dict[str, Any]
    
class WatermarkResponse(BaseModel):
    watermarked_content: str
    instance_id: str
    manifest: Dict[str, Any]
    embedding_time_ms: float
    
class VerificationRequest(BaseModel):
    content: str
    manifest: Dict[str, Any]
    
class VerificationResponse(BaseModel):
    verified: bool
    confidence: float
    watermark_detected: bool
    signature_valid: bool
    manifest_valid: bool
    provenance_chain: List[Dict[str, Any]]
    details: Dict[str, Any]

# ============================================================================
# WATERMARKING ENGINE
# ============================================================================

class TextSealEngine:
    """C2PA-compliant cryptographic watermarking engine"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self._load_keys()
        
        # Watermarking methods
        self.embedding_methods = {
            'unicode_homoglyphs': self._embed_homoglyphs,
            'zero_width': self._embed_zero_width,
            'whitespace': self._embed_whitespace
        }
        
        self.extraction_methods = {
            'unicode_homoglyphs': self._extract_homoglyphs,
            'zero_width': self._extract_zero_width,
            'whitespace': self._extract_whitespace
        }
        
        # Unicode homoglyph mappings
        self.HOMOGLYPHS = {
            'a': ['а', 'ạ', 'ả', 'ã', 'ā', 'ă'],  # Cyrillic, Vietnamese, Latin extended
            'e': ['е', 'ẹ', 'ẻ', 'ẽ', 'ē', 'ĕ'],
            'o': ['о', 'ọ', 'ỏ', 'õ', 'ō', 'ŏ'],
            'i': ['і', 'ị', 'ỉ', 'ĩ', 'ī', 'ĭ'],
            'c': ['с', 'ç', 'ć', 'č', 'ĉ', 'ċ'],
            'p': ['р', 'ṗ', 'ṕ', 'ṗ', 'ƥ', 'ᵱ'],
            'x': ['х', 'ẋ', 'ẍ', 'ẋ', 'ᶍ', '×'],
            'y': ['у', 'ỵ', 'ỷ', 'ỹ', 'ȳ', 'ẏ'],
            's': ['ѕ', 'ṡ', 'ṣ', 'š', 'ś', 'ŝ'],
            'n': ['п', 'ṅ', 'ṇ', 'ñ', 'ń', 'ň'],
        }
        
        # Reverse mapping for extraction
        self.HOMOGLYPHS_REVERSE = {}
        for original, variants in self.HOMOGLYPHS.items():
            for variant in variants:
                self.HOMOGLYPHS_REVERSE[variant] = original
    
    def _load_keys(self):
        """Load RSA keys for signing"""
        private_key_path = os.getenv(
            "TEXTSEAL_PRIVATE_KEY_PATH",
            "/etc/xoenovai/certs/textseal-private-key.pem"
        )
        
        try:
            with open(private_key_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            self.public_key = self.private_key.public_key()
            logger.info("TextSeal keys loaded successfully")
            
        except FileNotFoundError:
            logger.warning("TextSeal keys not found, generating new keys")
            self._generate_keys()
    
    def _generate_keys(self):
        """Generate new RSA key pair"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        logger.info("Generated new TextSeal RSA keys")
    
    async def watermark_content(
        self,
        content: str,
        metadata: Dict[str, Any],
        method: str = 'unicode_homoglyphs'
    ) -> tuple[str, Dict[str, Any], float]:
        """
        Watermark content with C2PA provenance
        
        Returns:
            (watermarked_content, c2pa_manifest, embedding_time_ms)
        """
        start_time = time.time()
        
        # Create C2PA manifest
        manifest = self._create_c2pa_manifest(content, metadata)
        
        # Sign manifest
        signature = self._sign_manifest(manifest)
        manifest['claim']['signature'] = {
            "algorithm": "RSA-PSS",
            "hash_algorithm": "SHA-256",
            "key_size": 4096,
            "signature_value": signature.hex()
        }
        
        # Generate watermark payload
        watermark_bits = self._generate_watermark_bits(manifest)
        
        # Embed watermark
        embedding_method = self.embedding_methods.get(method, self._embed_homoglyphs)
        watermarked_content = embedding_method(content, watermark_bits)
        
        # Update manifest with embedding details
        manifest['watermark']['method'] = method
        manifest['watermark']['bits_embedded'] = len(watermark_bits)
        manifest['watermark']['embedded_at'] = datetime.utcnow().isoformat() + 'Z'
        
        embedding_time_ms = (time.time() - start_time) * 1000
        
        # Metrics
        watermark_embedding_duration.labels(method=method).observe(embedding_time_ms / 1000)
        watermark_operations_total.labels(operation='embed').inc()
        
        logger.info(
            f"Content watermarked: instance_id={manifest['instance_id']}, "
            f"method={method}, time={embedding_time_ms:.2f}ms"
        )
        
        return watermarked_content, manifest, embedding_time_ms
    
    def _create_c2pa_manifest(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create C2PA content provenance manifest"""
        
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        instance_id = f"urn:uuid:{uuid.uuid4()}"
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        manifest = {
            "version": "1.3",
            "claim_generator": "Xoe-NovAi/1.0.0",
            "title": metadata.get("title", "AI Generated Content"),
            "format": "text/plain",
            "instance_id": instance_id,
            
            "claim": {
                "dc:title": metadata.get("title", "AI Generated Text"),
                "dc:format": "text/plain",
                "dc:creator": "Xoe-NovAi LLM Service",
                "dcterms:created": timestamp,
                
                "assertions": [
                    {
                        "label": "c2pa.ai-generative-training",
                        "data": {
                            "model_name": metadata.get("model", "unknown"),
                            "model_version": metadata.get("model_version", "1.0.0"),
                            "training_cutoff": metadata.get("training_cutoff", "2025-01-31"),
                            "fine_tuned": metadata.get("fine_tuned", False)
                        }
                    },
                    {
                        "label": "c2pa.ai-generative-metadata",
                        "data": {
                            "prompt_hash": hashlib.sha256(
                                metadata.get("prompt", "").encode()
                            ).hexdigest(),
                            "temperature": metadata.get("temperature", 0.7),
                            "max_tokens": metadata.get("max_tokens", 2048),
                            "top_p": metadata.get("top_p", 0.9),
                            "generation_timestamp": timestamp,
                            "user_id": metadata.get("user_id", "unknown")
                        }
                    },
                    {
                        "label": "c2pa.hash.data",
                        "data": {
                            "algorithm": "SHA-256",
                            "hash": content_hash,
                            "padded": False
                        }
                    },
                    {
                        "label": "c2pa.actions",
                        "data": {
                            "actions": [
                                {
                                    "action": "c2pa.created",
                                    "when": timestamp,
                                    "software_agent": "Xoe-NovAi/1.0.0",
                                    "changes": [
                                        {
                                            "description": "AI content generation",
                                            "reason": "User request"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            
            "watermark": {
                "method": "",  # Will be set during embedding
                "strength": "imperceptible",
                "bits_embedded": 0,  # Will be set during embedding
                "embedded_at": "",  # Will be set during embedding
                "verification_endpoint": "https://verify.xoenovai.com/api/v1/verify"
            }
        }
        
        return manifest
    
    def _sign_manifest(self, manifest: Dict[str, Any]) -> bytes:
        """Sign manifest with private key"""
        
        # Serialize claim for signing (exclude signature field if present)
        claim = manifest['claim'].copy()
        if 'signature' in claim:
            del claim['signature']
        
        manifest_json = json.dumps(
            claim,
            sort_keys=True,
            separators=(',', ':')
        )
        
        # Sign with RSA-PSS
        signature = self.private_key.sign(
            manifest_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    def _generate_watermark_bits(self, manifest: Dict[str, Any]) -> str:
        """Generate watermark bit string from manifest"""
        
        # Create watermark payload from instance_id and content hash
        payload = f"{manifest['instance_id']}:{manifest['claim']['assertions'][2]['data']['hash']}"
        payload_hash = hashlib.sha256(payload.encode()).digest()
        
        # Convert to binary string
        watermark_bits = ''.join(format(byte, '08b') for byte in payload_hash)
        
        # Use first 256 bits for stronger watermark
        return watermark_bits[:256]
    
    def _embed_homoglyphs(self, content: str, watermark_bits: str) -> str:
        """Embed watermark using Unicode homoglyph substitution"""
        
        result = []
        bit_index = 0
        
        for char in content:
            char_lower = char.lower()
            
            # Check if character has homoglyph variants
            if char_lower in self.HOMOGLYPHS and bit_index < len(watermark_bits):
                if watermark_bits[bit_index] == '1':
                    # Use homoglyph variant
                    variants = self.HOMOGLYPHS[char_lower]
                    variant = variants[min(int(watermark_bits[bit_index:bit_index+3], 2), len(variants)-1)]
                    result.append(variant if char.islower() else variant.upper())
                else:
                    # Keep original
                    result.append(char)
                bit_index += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _embed_zero_width(self, content: str, watermark_bits: str) -> str:
        """Embed watermark using zero-width characters"""
        
        ZERO_WIDTH_CHARS = {
            '00': '\u200B',  # Zero-width space
            '01': '\u200C',  # Zero-width non-joiner
            '10': '\u200D',  # Zero-width joiner
            '11': '\uFEFF',  # Zero-width no-break space
        }
        
        words = content.split(' ')
        result = []
        bit_index = 0
        
        for i, word in enumerate(words):
            result.append(word)
            
            if bit_index < len(watermark_bits) - 1:
                # Embed 2 bits between words
                bits = watermark_bits[bit_index:bit_index+2]
                if len(bits) == 2:
                    result.append(ZERO_WIDTH_CHARS[bits])
                bit_index += 2
            
            if i < len(words) - 1:
                result.append(' ')
        
        return ''.join(result)
    
    def _embed_whitespace(self, content: str, watermark_bits: str) -> str:
        """Embed watermark using whitespace patterns"""
        
        sentences = content.split('. ')
        result = []
        bit_index = 0
        
        for i, sentence in enumerate(sentences):
            result.append(sentence)
            
            if i < len(sentences) - 1:
                if bit_index < len(watermark_bits):
                    # One space for '0', two spaces for '1'
                    spaces = '  ' if watermark_bits[bit_index] == '1' else ' '
                    result.append('.' + spaces)
                    bit_index += 1
                else:
                    result.append('. ')
        
        return ''.join(result)
    
    async def verify_watermark(
        self,
        content: str,
        manifest: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify watermark and manifest authenticity"""
        
        verification_start = time.time()
        
        # 1. Verify signature
        signature_valid = self._verify_signature(manifest)
        
        # 2. Extract watermark
        method = manifest['watermark']['method']
        extraction_method = self.extraction_methods.get(method, self._extract_homoglyphs)
        extracted_bits = extraction_method(content)
        
        # 3. Generate expected watermark
        expected_bits = self._generate_watermark_bits(manifest)
        
        # 4. Compare watermarks
        watermark_detected = len(extracted_bits) > 0
        watermark_match = extracted_bits == expected_bits
        
        # 5. Calculate confidence
        confidence = self._calculate_confidence(extracted_bits, expected_bits)
        
        # 6. Verify content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        content_hash_match = content_hash == manifest['claim']['assertions'][2]['data']['hash']
        
        # 7. Build provenance chain
        provenance_chain = self._build_provenance_chain(manifest)
        
        # Overall verification
        verified = signature_valid and watermark_match and content_hash_match
        
        verification_time_ms = (time.time() - verification_start) * 1000
        
        # Metrics
        if verified:
            watermark_verification_success.labels(method=method).inc()
        else:
            reason = "signature" if not signature_valid else "watermark" if not watermark_match else "content_hash"
            watermark_verification_failure.labels(method=method, reason=reason).inc()
        
        watermark_operations_total.labels(operation='verify').inc()
        
        return {
            "verified": verified,
            "confidence": confidence,
            "watermark_detected": watermark_detected,
            "signature_valid": signature_valid,
            "manifest_valid": signature_valid and content_hash_match,
            "provenance_chain": provenance_chain,
            "details": {
                "watermark_match": watermark_match,
                "content_hash_match": content_hash_match,
                "bits_extracted": len(extracted_bits),
                "bits_expected": len(expected_bits),
                "verification_time_ms": verification_time_ms
            }
        }
    
    def _verify_signature(self, manifest: Dict[str, Any]) -> bool:
        """Verify manifest cryptographic signature"""
        
        try:
            # Extract signature
            signature_hex = manifest['claim']['signature']['signature_value']
            signature = bytes.fromhex(signature_hex)
            
            # Reconstruct signed data
            claim = manifest['claim'].copy()
            del claim['signature']
            manifest_json = json.dumps(claim, sort_keys=True, separators=(',', ':'))
            
            # Verify signature
            self.public_key.verify(
                signature,
                manifest_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def _extract_homoglyphs(self, content: str) -> str:
        """Extract watermark from homoglyph-encoded content"""
        
        bits = []
        
        for char in content:
            char_lower = char.lower()
            
            # Check if character is a homoglyph
            if char_lower in self.HOMOGLYPHS_REVERSE:
                bits.append('1')  # Homoglyph detected
            elif char_lower in self.HOMOGLYPHS:
                bits.append('0')  # Original character
        
        return ''.join(bits)
    
    def _extract_zero_width(self, content: str) -> str:
        """Extract watermark from zero-width character encoding"""
        
        ZERO_WIDTH_REVERSE = {
            '\u200B': '00',
            '\u200C': '01',
            '\u200D': '10',
            '\uFEFF': '11',
        }
        
        bits = []
        
        for char in content:
            if char in ZERO_WIDTH_REVERSE:
                bits.append(ZERO_WIDTH_REVERSE[char])
        
        return ''.join(bits)
    
    def _extract_whitespace(self, content: str) -> str:
        """Extract watermark from whitespace patterns"""
        
        bits = []
        sentences = content.split('.')
        
        for i in range(len(sentences) - 1):
            # Check spacing after period
            if sentences[i].endswith('  ') or (i < len(sentences) - 1 and sentences[i+1].startswith('  ')):
                bits.append('1')
            else:
                bits.append('0')
        
        return ''.join(bits)
    
    def _calculate_confidence(self, extracted: str, expected: str) -> float:
        """Calculate watermark detection confidence"""
        
        if not extracted or not expected:
            return 0.0
        
        # Hamming distance-based confidence
        min_length = min(len(extracted), len(expected))
        matches = sum(1 for i in range(min_length) if extracted[i] == expected[i])
        
        confidence = matches / len(expected) if len(expected) > 0 else 0.0
        
        return round(confidence, 4)
    
    def _build_provenance_chain(self, manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build content provenance chain"""
        
        chain = []
        
        # Extract actions from manifest
        actions = manifest['claim'].get('assertions', [])
        for assertion in actions:
            if assertion.get('label') == 'c2pa.actions':
                for action in assertion['data']['actions']:
                    chain.append({
                        "action": action['action'],
                        "timestamp": action['when'],
                        "software_agent": action['software_agent'],
                        "description": action.get('changes', [{}])[0].get('description', '')
                    })
        
        return chain

# Global engine instance
textseal_engine = TextSealEngine()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "textseal",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/watermark", response_model=WatermarkResponse)
async def watermark_content(
    request: WatermarkRequest,
    background_tasks: BackgroundTasks,
    method: str = 'unicode_homoglyphs'
):
    """Watermark AI-generated content with C2PA provenance"""
    
    if method not in textseal_engine.embedding_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid method. Choose from: {list(textseal_engine.embedding_methods.keys())}"
        )
    
    try:
        watermarked_content, manifest, embedding_time_ms = await textseal_engine.watermark_content(
            content=request.content,
            metadata=request.metadata,
            method=method
        )
        
        # Store manifest in background (implement your storage logic)
        # background_tasks.add_task(store_manifest, manifest)
        
        return WatermarkResponse(
            watermarked_content=watermarked_content,
            instance_id=manifest['instance_id'],
            manifest=manifest,
            embedding_time_ms=embedding_time_ms
        )
        
    except Exception as e:
        logger.error(f"Watermarking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Watermarking failed: {str(e)}")

@app.post("/verify", response_model=VerificationResponse)
async def verify_watermark(request: VerificationRequest):
    """Verify watermarked content authenticity"""
    
    try:
        verification_result = await textseal_engine.verify_watermark(
            content=request.content,
            manifest=request.manifest
        )
        
        return VerificationResponse(**verification_result)
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.get("/manifest/{instance_id}")
async def get_manifest(instance_id: str):
    """Retrieve C2PA manifest by instance ID"""
    
    # Implement manifest retrieval from storage
    # This is a placeholder
    raise HTTPException(status_code=501, detail="Manifest retrieval not implemented")

@app.get("/metrics")
async def get_metrics():
    """Get watermarking metrics"""
    
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        ssl_keyfile=os.getenv("SSL_KEYFILE", "/etc/xoenovai/certs/server-key.pem"),
        ssl_certfile=os.getenv("SSL_CERTFILE", "/etc/xoenovai/certs/server-cert.pem")
    )
