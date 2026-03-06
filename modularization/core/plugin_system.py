"""
Plugin System for OpenCode Multi-Account System
===============================================

Provides a robust plugin architecture for extending the system with
custom providers, integrations, and services.
"""

import importlib
import inspect
import logging
import pkgutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Type, Callable, Union
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import time

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    loaded: bool = False
    load_time: Optional[float] = None
    error: Optional[str] = None


class PluginInterface(ABC):
    """Base interface for all plugins."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin and cleanup resources."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass


class ProviderPlugin(PluginInterface):
    """Base interface for provider plugins."""
    
    @abstractmethod
    async def get_response(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get response from the provider."""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get provider-specific metrics."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider health."""
        pass
    
    @abstractmethod
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        pass


class IntegrationPlugin(PluginInterface):
    """Base interface for integration plugins."""
    
    @abstractmethod
    async def start(self) -> bool:
        """Start the integration service."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the integration service."""
        pass
    
    @abstractmethod
    async def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle system events."""
        pass


class PluginRegistry:
    """Registry for managing plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, PluginInterface] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._initialized = False
        self._lock = threading.Lock()
    
    def register_plugin(self, name: str, plugin_class: Type[PluginInterface], metadata: PluginMetadata) -> None:
        """Register a plugin class."""
        with self._lock:
            self._metadata[name] = metadata
            self._dependencies[name] = metadata.dependencies
            logger.info(f"Registered plugin: {name} v{metadata.version}")
    
    def load_plugin(self, name: str, config: Dict[str, Any]) -> bool:
        """Load and initialize a plugin."""
        with self._lock:
            if name not in self._metadata:
                logger.error(f"Plugin {name} not registered")
                return False
            
            metadata = self._metadata[name]
            if not metadata.enabled:
                logger.info(f"Plugin {name} is disabled")
                return True
            
            try:
                # Check dependencies
                if not self._check_dependencies(name):
                    logger.error(f"Plugin {name} has unsatisfied dependencies")
                    return False
                
                # Import and instantiate plugin
                plugin_class = self._get_plugin_class(name)
                plugin = plugin_class()
                
                # Initialize plugin
                start_time = time.time()
                success = plugin.initialize(config)
                load_time = time.time() - start_time
                
                if success:
                    self._plugins[name] = plugin
                    metadata.loaded = True
                    metadata.load_time = load_time
                    logger.info(f"Successfully loaded plugin: {name} (took {load_time:.2f}s)")
                    return True
                else:
                    metadata.error = "Initialization failed"
                    logger.error(f"Failed to initialize plugin: {name}")
                    return False
                    
            except Exception as e:
                metadata.error = str(e)
                logger.error(f"Error loading plugin {name}: {e}", exc_info=True)
                return False
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        with self._lock:
            if name not in self._plugins:
                logger.warning(f"Plugin {name} not loaded")
                return False
            
            try:
                plugin = self._plugins[name]
                plugin.shutdown()
                del self._plugins[name]
                
                if name in self._metadata:
                    self._metadata[name].loaded = False
                
                logger.info(f"Unloaded plugin: {name}")
                return True
                
            except Exception as e:
                logger.error(f"Error unloading plugin {name}: {e}", exc_info=True)
                return False
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get a loaded plugin instance."""
        return self._plugins.get(name)
    
    def get_provider_plugin(self, name: str) -> Optional[ProviderPlugin]:
        """Get a provider plugin instance."""
        plugin = self.get_plugin(name)
        return plugin if isinstance(plugin, ProviderPlugin) else None
    
    def get_integration_plugin(self, name: str) -> Optional[IntegrationPlugin]:
        """Get an integration plugin instance."""
        plugin = self.get_plugin(name)
        return plugin if isinstance(plugin, IntegrationPlugin) else None
    
    def list_plugins(self) -> List[PluginMetadata]:
        """List all registered plugins."""
        return list(self._metadata.values())
    
    def list_loaded_plugins(self) -> List[str]:
        """List all loaded plugins."""
        return list(self._plugins.keys())
    
    def list_provider_plugins(self) -> List[str]:
        """List all provider plugins."""
        return [name for name, metadata in self._metadata.items() 
                if issubclass(self._get_plugin_class(name), ProviderPlugin)]
    
    def list_integration_plugins(self) -> List[str]:
        """List all integration plugins."""
        return [name for name, metadata in self._metadata.items() 
                if issubclass(self._get_plugin_class(name), IntegrationPlugin)]
    
    def shutdown_all(self) -> None:
        """Shutdown all loaded plugins."""
        with self._lock:
            for name in list(self._plugins.keys()):
                self.unload_plugin(name)
    
    def _check_dependencies(self, name: str) -> bool:
        """Check if all dependencies for a plugin are loaded."""
        dependencies = self._dependencies.get(name, [])
        for dep in dependencies:
            if dep not in self._plugins:
                logger.error(f"Dependency {dep} not loaded for plugin {name}")
                return False
        return True
    
    def _get_plugin_class(self, name: str) -> Type[PluginInterface]:
        """Get the plugin class for a given name."""
        # This would need to be implemented based on your plugin discovery mechanism
        # For now, return a placeholder
        return PluginInterface


class PluginLoader:
    """Handles automatic discovery and loading of plugins."""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self._discovered_plugins: Dict[str, Dict[str, Any]] = {}
    
    def discover_plugins_in_package(self, package_name: str) -> None:
        """Discover plugins in a Python package."""
        try:
            package = importlib.import_module(package_name)
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
                if not is_pkg:
                    self._discover_plugins_in_module(name)
        except ImportError as e:
            logger.warning(f"Could not import package {package_name}: {e}")
    
    def discover_plugins_in_directory(self, directory: Union[str, Path]) -> None:
        """Discover plugins in a directory."""
        directory = Path(directory)
        if not directory.exists():
            logger.warning(f"Directory {directory} does not exist")
            return
        
        # Add directory to Python path temporarily
        import sys
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
        
        # Discover plugins in Python files
        for py_file in directory.glob("*.py"):
            if py_file.name != "__init__.py":
                module_name = py_file.stem
                try:
                    self._discover_plugins_in_module(module_name)
                except Exception as e:
                    logger.warning(f"Error discovering plugins in {module_name}: {e}")
    
    def load_all_plugins(self, config: Dict[str, Any]) -> Dict[str, bool]:
        """Load all discovered plugins."""
        results = {}
        for name in self._discovered_plugins:
            results[name] = self.registry.load_plugin(name, config)
        return results
    
    def _discover_plugins_in_module(self, module_name: str) -> None:
        """Discover plugins in a Python module."""
        try:
            module = importlib.import_module(module_name)
            
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface and
                    obj != ProviderPlugin and
                    obj != IntegrationPlugin):
                    
                    # Get metadata from class
                    metadata = self._extract_metadata(obj)
                    self.registry.register_plugin(name, obj, metadata)
                    self._discovered_plugins[name] = {
                        'module': module_name,
                        'class': obj
                    }
                    
        except ImportError as e:
            logger.warning(f"Could not import module {module_name}: {e}")
    
    def _extract_metadata(self, plugin_class: Type[PluginInterface]) -> PluginMetadata:
        """Extract metadata from a plugin class."""
        # Try to get metadata from class attributes or docstring
        name = getattr(plugin_class, '__plugin_name__', plugin_class.__name__)
        version = getattr(plugin_class, '__version__', '1.0.0')
        description = getattr(plugin_class, '__description__', plugin_class.__doc__ or '')
        author = getattr(plugin_class, '__author__', 'Unknown')
        dependencies = getattr(plugin_class, '__dependencies__', [])
        
        return PluginMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            dependencies=dependencies
        )


class PluginManager:
    """Main plugin manager for the system."""
    
    def __init__(self):
        self.registry = PluginRegistry()
        self.loader = PluginLoader(self.registry)
        self._initialized = False
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin system."""
        if self._initialized:
            return True
        
        try:
            # Discover built-in plugins
            self._discover_builtin_plugins()
            
            # Discover external plugins
            plugin_paths = config.get('plugin_paths', [])
            for path in plugin_paths:
                self.loader.discover_plugins_in_directory(path)
            
            # Load all plugins
            load_results = self.loader.load_all_plugins(config)
            
            # Check for critical plugin failures
            failed_plugins = [name for name, success in load_results.items() if not success]
            if failed_plugins:
                logger.warning(f"Some plugins failed to load: {failed_plugins}")
            
            self._initialized = True
            logger.info(f"Plugin system initialized with {len(load_results)} plugins")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize plugin system: {e}", exc_info=True)
            return False
    
    def shutdown(self) -> None:
        """Shutdown the plugin system."""
        if not self._initialized:
            return
        
        self.registry.shutdown_all()
        self._initialized = False
        logger.info("Plugin system shutdown complete")
    
    def get_provider_manager(self) -> 'ProviderManager':
        """Get the provider manager."""
        return ProviderManager(self.registry)
    
    def get_integration_manager(self) -> 'IntegrationManager':
        """Get the integration manager."""
        return IntegrationManager(self.registry)
    
    def _discover_builtin_plugins(self) -> None:
        """Discover built-in plugins."""
        # This would discover plugins in the providers/ and integrations/ directories
        builtin_paths = [
            Path(__file__).parent.parent / "providers",
            Path(__file__).parent.parent / "integrations"
        ]
        
        for path in builtin_paths:
            if path.exists():
                self.loader.discover_plugins_in_directory(path)


class ProviderManager:
    """Manager for provider plugins."""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
    
    async def get_response(self, prompt: str, preferred_provider: Optional[str] = None, 
                          context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get response from the best available provider."""
        providers = self._get_available_providers()
        
        if not providers:
            return {"error": "No providers available", "status": "error"}
        
        # If preferred provider specified, try it first
        if preferred_provider and preferred_provider in providers:
            try:
                response = await providers[preferred_provider].get_response(prompt, context)
                if response.get("status") != "error":
                    return response
            except Exception as e:
                logger.warning(f"Preferred provider {preferred_provider} failed: {e}")
        
        # Try providers in order of preference/availability
        for name, provider in providers.items():
            try:
                response = await provider.get_response(prompt, context)
                if response.get("status") != "error":
                    return response
            except Exception as e:
                logger.warning(f"Provider {name} failed: {e}")
        
        return {"error": "All providers failed", "status": "error"}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from all providers."""
        metrics = {}
        providers = self._get_available_providers()
        
        for name, provider in providers.items():
            try:
                provider_metrics = await provider.get_metrics()
                metrics[name] = provider_metrics
            except Exception as e:
                logger.error(f"Failed to get metrics from provider {name}: {e}")
                metrics[name] = {"error": str(e)}
        
        return metrics
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers."""
        health = {}
        providers = self._get_available_providers()
        
        for name, provider in providers.items():
            try:
                health[name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for provider {name}: {e}")
                health[name] = False
        
        return health
    
    def _get_available_providers(self) -> Dict[str, ProviderPlugin]:
        """Get all available provider plugins."""
        providers = {}
        for name in self.registry.list_provider_plugins():
            plugin = self.registry.get_provider_plugin(name)
            if plugin:
                providers[name] = plugin
        return providers


class IntegrationManager:
    """Manager for integration plugins."""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self._running_integrations: List[str] = []
    
    async def start_all(self) -> bool:
        """Start all integration plugins."""
        integrations = self._get_available_integrations()
        
        for name, integration in integrations.items():
            try:
                success = await integration.start()
                if success:
                    self._running_integrations.append(name)
                    logger.info(f"Started integration: {name}")
                else:
                    logger.warning(f"Failed to start integration: {name}")
            except Exception as e:
                logger.error(f"Error starting integration {name}: {e}")
        
        return len(self._running_integrations) > 0
    
    async def stop_all(self) -> None:
        """Stop all running integrations."""
        for name in self._running_integrations:
            try:
                integration = self.registry.get_integration_plugin(name)
                if integration:
                    await integration.stop()
                    logger.info(f"Stopped integration: {name}")
            except Exception as e:
                logger.error(f"Error stopping integration {name}: {e}")
        
        self._running_integrations.clear()
    
    async def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle system events in all integrations."""
        integrations = self._get_available_integrations()
        
        for name, integration in integrations.items():
            try:
                await integration.handle_event(event_type, data)
            except Exception as e:
                logger.error(f"Error handling event in integration {name}: {e}")
    
    def _get_available_integrations(self) -> Dict[str, IntegrationPlugin]:
        """Get all available integration plugins."""
        integrations = {}
        for name in self.registry.list_integration_plugins():
            plugin = self.registry.get_integration_plugin(name)
            if plugin:
                integrations[name] = plugin
        return integrations


# Global plugin manager instance
plugin_manager = PluginManager()