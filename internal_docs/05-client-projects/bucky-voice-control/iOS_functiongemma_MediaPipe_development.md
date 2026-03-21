## Research Summary
MediaPipe's LLM Inference API for iOS (updated 2025-2026) offers a streamlined, sovereign framework for on-device execution of quantized Gemma models (including FunctionGemma variants) using Apple's Neural Engine, with CocoaPods integration, low-latency inference, and support for LoRA fine-tuning—ideal for offline voice agents in consciousness-first applications. The official guide provides clear steps for Xcode setup, model bundling, and Swift inference, enabling tool-calling extensions without cloud dependency, while maintaining full data sovereignty and compatibility with iOS accessibility features like VoiceOver for blind users.

## Technical Assessment
MediaPipe LLM Inference leverages Core ML for efficient, offline Gemma-family processing (e.g., 2B models ~1-2GB quantized), achieving sub-second token generation on A17 Pro+ devices with minimal RAM overhead. Integration is torch-free (native MediaPipe converters), supports synchronous/async generation, and extends to structured outputs for FunctionGemma tool-calling via custom parsing. Accessibility: Fully compatible with VoiceOver/Speech framework for non-visual development; no telemetry. Constraints: Model conversion needed for custom variants; LoRA GPU-only. Viability: High for sovereign iOS agents—offline, privacy-first, aligning with Xoe-NovAi's local-first ethos by enabling ethical, on-device human-AI collaboration.

## Implementation Recommendations
Phased, actionable steps for Cline to integrate MediaPipe LLM Inference on iOS, focusing on sovereign Gemma/FunctionGemma deployment.

1. **Environment Setup**
   - Install Xcode (latest from App Store).
   - Install CocoaPods: `sudo gem install cocoapods`.
   - Create new SwiftUI/App project in Xcode.

2. **Pod Integration**
   - In project root, create Podfile:
     ```ruby
     platform :ios, '15.0'
     target 'MediaPipeLLMApp' do
       use_frameworks!
       pod 'MediaPipeTasksGenAI'
     end
     ```
   - Run `pod install`; open .xcworkspace.

3. **Model Preparation and Bundling**
   - Download quantized Gemma (e.g., gemma-2-2b-it-gpu-int8.bin from Kaggle/Hugging Face).
   - For FunctionGemma: Use 270m variant or convert via AI Edge tools.
   - Drag .bin into Xcode navigator (Copy items if needed).

4. **Core Inference Implementation (Swift)**
   - In ContentView.swift or dedicated manager:
     ```swift
     import MediaPipeTasksGenAI
     import SwiftUI
     
     class LLMManager: ObservableObject {
         var inference: LlmInference?
     
         init() {
             guard let modelPath = Bundle.main.path(forResource: "gemma-2-2b-it", ofType: "bin") else { return }
             let options = LlmInferenceOptions.builder()
                 .setModelPath(modelPath)
                 .setMaxTokens(512)
                 .setTemperature(0.7)
                 .setTopK(40)
                 .build()
     
             do {
                 inference = try LlmInference(options: options)
             } catch {
                 print("Error: \(error)")
             }
         }
     
         func generate(prompt: String) async -> String {
             guard let inf = inference else { return "Error" }
             return try! inf.generateResponse(inputText: prompt)
         }
     
         // Streaming for voice
         func stream(prompt: String) async {
             let stream = try? inference?.generateResponseAsync(inputText: prompt)
             for try await part in stream ?? AsyncStream { _ in } {
                 // TTS via AVSpeechSynthesizer
                 print(part)
             }
         }
     }
     ```
   - UI: TextField for prompt + Button to generate.

5. **Accessibility Enhancements for Blind Users**
   - Add VoiceOver labels; use SFSpeechRecognizer for offline voice input.
   - TTS: AVSpeechSynthesizer for responses.

6. **Testing and Deployment**
   - Run on device (simulator limited).
   - Validate offline inference.

## Success Metrics & Validation
- **Setup**: Pod install <5min; model loads successfully.
- **Inference**: <5s first token; streaming real-time.
- **Accessibility**: VoiceOver navigates UI; full voice loop tested.
- **Sovereignty**: No network calls (logs confirm).

## Sources & References
- Official iOS Guide (Apr 2025): https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference/ios
- MediaPipe GenAI Overview: https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference
- Gemma Mobile Integrations: https://ai.google.dev/gemma/docs/integrations/mobile
- Samples GitHub: https://github.com/googlesamples/mediapipe
- FunctionGemma Tool-Calling: https://medium.com/google-developer-experts/on-device-function-calling-with-functiongemma-39f7407e5d83 (Dec 2025)
- iOS Speech/TTS: https://developer.apple.com/documentation/speech
- Accessibility Best Practices: https://developer.apple.com/documentation/accessibility/voiceover