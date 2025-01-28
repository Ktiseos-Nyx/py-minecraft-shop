"""
SimpleChestShop - A PySpigot plugin for creating simple chest shops in Minecraft.

This plugin allows players to create chest shops by placing signs on chests,
enabling item trading with other players using server currency (via Vault).
Integrates with TownyAdvanced for town-based shop restrictions and LuckPerms
for permission control.
"""
import os  # Standard library imports FIRST
import yaml

from spigotmc import (  # spigotmc imports next - Grouped and broken into lines
    plugin,
    event,
    Action,
    Material
)

from com.palmergames.bukkit.towny import TownyUniverse  # com.palmergames imports next
from net.milkbowl.vault.economy import Economy  # net.milkbowl imports next

from org.bukkit import (  # org.bukkit imports last - Grouped and broken into lines
    Material,
    Action
)
# Removed: from org.bukkit.plugin import RegisteredServiceProvider - Unused import removed


# --- Configuration ---
config = {}  # Global configuration dictionary - Correct variable name style
VAULT_ENABLED = False  # Global flag to track if Vault is enabled (RENAMED to UPPER_CASE)
VAULT_ECONOMY = None  # Global variable to store the Vault Economy service (RENAMED to UPPER_CASE)


def load_config():
    """Loads the plugin configuration from config.yml or creates a default config if not found."""
    global config
    config_file_path = "plugins/PySpigot/scripts/SimpleChestShop/config.yml"
    default_config = {  # Define our default configuration as a Python dictionary
        "settings": {
            "enable_shop_creation": True,
            "debug_mode": False
        },
        "messages": {
            "shop_detected": "§a[Shop] System: Shop sign detected and enabled!",
            "no_shop_permission": "§c[Shop] System: You do not have permission to create shops."
        },
        "towny": {
            "enable_towny_integration": True,
            "require_town": False
        },
        "permissions": {
            "enable_permissions": True,
            "create_shop_permission": "chestshop.create"
        },
        "vault": {
            "enable_vault_integration": True
        }
    }

    if not os.path.exists(config_file_path):  # Check if config.yml file exists
        print "[SimpleChestShop] config.yml not found, creating default..." # Python 2.7 print statement (no parentheses)
        config = default_config  # Use the default config
        with open(config_file_path, "w") as config_file: # Renamed 'f' to 'config_file'
            yaml.dump(default_config, config_file, indent=2)  # Save default config to file
    else:
        try:
            with open(config_file_path, "r") as config_file: # Renamed 'f' to 'config_file'
                config = yaml.safe_load(config_file)
        except FileNotFoundError:  # Catch specific FileNotFoundError
            print "[SimpleChestShop] config.yml not found, creating default..." # Python 2.7 print statement (no parentheses)
            config = default_config
            with open(config_file_path, "w") as config_file: # Renamed 'f' to 'config_file'
                yaml.dump(default_config, config_file, indent=2)
        except yaml.YAMLError, exception:  # Catch specific yaml.YAMLError for YAML parsing errors # Renamed 'e' to 'exception' # Python 2.7 syntax for except
            print "[SimpleChestShop] Error parsing config.yml (YAML error): {}".format(exception)  # Use .format() for Python 2.7 # Python 2.7 print statement (no parentheses)
            print "[SimpleChestShop] Using default configuration." # Python 2.7 print statement (no parentheses)
            config = default_config
        except Exception, exception:  # Catch any *other* unexpected exceptions (still broad, but less so) # Renamed 'e' to 'exception' # Python 2.7 syntax for except
            print "[SimpleChestShop] Unexpected error loading config.yml: {}".format(exception)  # Use .format() for Python 2.7 # Python 2.7 print statement (no parentheses)
            print "[SimpleChestShop] Using default configuration." # Python 2.7 print statement (no parentheses)
            config = default_config

    # After loading (or creating) config, merge defaults to ensure all settings exist
    config = dict(default_config.items() + (config or {}).items())  # Python 2.7 dict merge - slightly different syntax

    print "[SimpleChestShop] Configuration loaded."  # Indicate config loading is complete # Python 2.7 print statement (no parentheses)
    if config.get("settings", {}).get("debug_mode", False):  # Example of using debug_mode from config
        print "[SimpleChestShop] Debug mode is enabled." # Python 2.7 print statement (no parentheses)


def get_vault_economy():  # New function to get Vault Economy service
    """Retrieves the Vault economy service."""
    global VAULT_ECONOMY, VAULT_ENABLED
    if not config.get("vault", {}).get("enable_vault_integration", True):  # Check if Vault integration is enabled in config
        print "[SimpleChestShop] Vault integration is disabled in config." # Python 2.7 print statement (no parentheses)
        VAULT_ENABLED = False
        return None  # Vault integration disabled

    if server.getPluginManager().getPlugin("Vault") is None:  # Correctly using 'server'
        print "[SimpleChestShop] Vault plugin not found! Disabling Vault integration." # Python 2.7 print statement (no parentheses)
        VAULT_ENABLED = False
        return None  # Vault not found

    rsp = server.getServicesManager().getRegistration(Economy)  # Correctly using 'server'

    if rsp is None:  # Check if Economy service is registered
        print "[SimpleChestShop] Vault Economy service not found! Disabling Vault integration." # Python 2.7 print statement (no parentheses)
        VAULT_ENABLED = False
        return None  # Economy service not found

    VAULT_ECONOMY = rsp.getProvider()  # Get the Economy provider
    if VAULT_ECONOMY is not None:
        VAULT_ENABLED = True
        print "[SimpleChestShop] Vault integration enabled. Economy provider: {}".format(VAULT_ECONOMY.getName())  # Use .format() for Python 2.7 # Python 2.7 print statement (no parentheses)
        return VAULT_ECONOMY

    # No 'else' needed here!  If we reach this point, it means the 'if' condition was false.
    print "[SimpleChestShop] Failed to get Vault Economy provider! Disabling Vault integration."  # Corrected line break (though not strictly needed here) # Python 2.7 print statement (no parentheses)
    VAULT_ENABLED = False
    return None


# --- Helper Functions ---

def is_in_town(location):
    """Checks if the location is within a town."""
    try:
        return TownyUniverse.getInstance().getTownBlock(location).hasTown()  # Use hasTown() instead of is not None
    except Exception, exception:  # Catch general Exception for Towny API errors (consider more specific if you know the type) # Renamed 'e' to 'exception' # Python 2.7 syntax for except
        print "[SimpleChestShop] Error checking Towny location: {}".format(exception)  # Use .format() for Python 2.7 # Python 2.7 print statement (no parentheses)
        return False


# --- Event Handlers ---

@event("block.SignChangeEvent")
def on_sign_change(event):
    """Handles the sign change event to create chest shops."""
    player = event.getPlayer()
    lines = event.getLines()
    location = event.getBlock().getLocation()

    if lines[0].lower() == "[shop]":
        if config.get("permissions", {}).get("enable_permissions", True):  # Check if permission checks are enabled
            create_perm = config.get("permissions", {}).get("create_shop_permission",
                                                            "chestshop.create")  # Get permission node from config
            if not player.hasPermission(create_perm):  # Check if player has the create shop permission
                message = config.get("messages", {}).get("no_shop_permission",
                                                        "§c[Shop] System: You do not have permission to create shops.")
                player.sendMessage(message)
                event.setCancelled(True)  # Cancel sign creation
                return  # Stop processing

        if not config.get(  # Corrected indentation - Added 1 space for continued line
                "towny", {}
        ).get(
                "enable_towny_integration",
                True
        ):
            pass
        elif config.get("towny", {}).get("require_town", False):
            if not is_in_town(location):  # Corrected indentation - Removed extra indentation
                message = config.get("messages", {}).get("shop_must_be_in_town",  # Corrected indentation - Removed extra indentation
                                                        "§c[Shop] System: Shops can only be created within town boundaries.")
                player.sendMessage(message)
                event.setCancelled(True)
                return

        if config.get("settings", {}).get("enable_shop_creation", True):  # Check if shop creation is enabled in general
            message = config.get("messages", {}).get("shop_detected", "§a[Shop] System: Shop sign detected and enabled!")
            player.sendMessage(message)
        else:
            player.sendMessage("§c[Shop] System: Shop creation is currently disabled by the server.")
            event.setCancelled(True)


@event("player.PlayerInteractEvent")
def on_player_interact(event):
    """Handles player interaction events, specifically right-clicking chests."""
    # This function will be called when a player interacts with something
    if event.getAction() == Action.RIGHT_CLICK_BLOCK:  # Check if it's a right-click on a block
        block = event.getClickedBlock()
        if block.getType() == Material.CHEST:  # Check if the block is a chest
            player = event.getPlayer()
            player.sendMessage("§bChest right-clicked!")  # Send a message to the player


# --- Plugin Class ---

@plugin("SimpleChestShop")  # This name will be used to identify your plugin
class SimpleChestShopPlugin:
    """Main plugin class for SimpleChestShop."""

    def on_enable(self):
        """Called when the plugin is enabled."""
        load_config()  # Load the configuration when the plugin starts
        print "[SimpleChestShop] Plugin enabled!" # Python 2.7 print statement (no parentheses)
        get_vault_economy()  # Call get_vault_economy() on plugin enable to detect and get Vault

    def on_disable(self):
        """Called when the plugin is disabled."""
        print "[SimpleChestShop] Plugin disabled!" # Python 2.7 print statement (no parentheses)
