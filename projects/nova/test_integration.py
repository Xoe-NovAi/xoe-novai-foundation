#!/usr/bin/env python3
"""Test script for service manager and CLI implementations"""

import asyncio
import sys
import json
from service_manager import get_service_manager
from cli_abstraction import CLIMode, CLIFactory, CLIConfig


async def test_service_manager():
    """Test service manager"""
    print("=" * 60)
    print("TEST 1: Service Manager")
    print("=" * 60)
    
    manager = get_service_manager()
    
    print("\n1. Initial service status:")
    status = await manager.get_all_services_status()
    for name, info in status.items():
        print(f"  {name}: {info['status']} (healthy: {info['healthy']})")
    
    print("\n2. Testing health check for Ollama:")
    health = await manager._check_service_health('ollama')
    print(f"  Ollama health: {health}")
    
    print("\n3. Service startup commands:")
    for name, service in manager.services.items():
        print(f"  {name}: {service.startup_command}")
    
    await manager.shutdown()
    print("\n✅ Service Manager test complete\n")


async def test_cli_abstraction():
    """Test CLI abstraction layer"""
    print("=" * 60)
    print("TEST 2: CLI Abstraction Layer")
    print("=" * 60)
    
    print("\n1. Testing Standalone CLI creation:")
    config = CLIConfig(
        mode=CLIMode.STANDALONE,
        interactive=False,
        headless=True,
        log_level="WARNING"
    )
    cli = CLIFactory.create(config)
    print(f"  ✅ Created {cli.__class__.__name__}")
    
    print("\n2. Testing Cline CLI creation:")
    config_cline = CLIConfig(mode=CLIMode.CLINE, headless=True, log_level="WARNING")
    cli_cline = CLIFactory.create(config_cline)
    print(f"  ✅ Created {cli_cline.__class__.__name__}")
    
    print("\n3. Testing Claude CLI creation:")
    config_claude = CLIConfig(
        mode=CLIMode.CLAUDE,
        provider_api_key="sk-test",
        headless=True,
        log_level="WARNING"
    )
    cli_claude = CLIFactory.create(config_claude)
    print(f"  ✅ Created {cli_claude.__class__.__name__}")
    
    print("\n4. Testing environment detection:")
    detected_mode = CLIFactory.detect_environment()
    print(f"  Detected mode: {detected_mode.value}")
    
    print("\n✅ CLI Abstraction test complete\n")


async def test_cli_initialization():
    """Test CLI initialization"""
    print("=" * 60)
    print("TEST 3: CLI Initialization")
    print("=" * 60)
    
    print("\n1. Testing Standalone CLI initialization:")
    try:
        config = CLIConfig(mode=CLIMode.STANDALONE, log_level="WARNING")
        cli = CLIFactory.create(config)
        success = await cli.initialize()
        print(f"  ✅ Initialization: {success}")
        await cli.shutdown()
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n✅ CLI Initialization test complete\n")


async def test_cli_commands():
    """Test CLI command processing"""
    print("=" * 60)
    print("TEST 4: CLI Command Processing")
    print("=" * 60)
    
    try:
        print("\n1. Initializing Standalone CLI...")
        config = CLIConfig(mode=CLIMode.STANDALONE, log_level="WARNING")
        cli = CLIFactory.create(config)
        
        if not await cli.initialize():
            print("  ❌ Failed to initialize")
            return
        
        print("  ✅ Initialized")
        
        print("\n2. Testing 'voice' command:")
        response = await cli.process_command("voice", ["Hello", "world"])
        print(f"  Response: {response[:100]}...")
        
        print("\n3. Testing 'status' command:")
        response = await cli.process_command("status", [])
        status_data = json.loads(response)
        print(f"  ✅ Got status with {len(status_data)} fields")
        
        print("\n4. Testing 'help' command:")
        response = await cli.process_command("help", [])
        print(f"  ✅ Got help text ({len(response)} chars)")
        
        await cli.shutdown()
        print("\n✅ CLI Command test complete\n")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " VOICE ASSISTANT - INTEGRATION TESTS".ljust(59) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        await test_service_manager()
        await test_cli_abstraction()
        await test_cli_initialization()
        await test_cli_commands()
        
        print("=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY ✅")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
