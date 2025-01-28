from spigotmc import *
import yaml
import os  # Import the 'os' module for file system operations
from com.palmergames.bukkit.towny import TownyUniverse # Import TownyUniverse for town checking
from org.bukkit import Material, Action # Import Material and Action for block and action checking


# --- Configuration ---
config = {}

def load_config():
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
        }
    }

    if not os.path.exists(config_file_path): # Check if config.yml file exists
        print("[SimpleChestShop] config.yml not found, creating default...")
        config = default_config  # Use the default config
        with open(config_file_path, "w") as f:
            yaml.dump(default_config, f, indent=2) # Save default config to file
    else:
        try:
            with open(config_file_path, "r") as f:
                config = yaml.safe_load(f)
        except Exception as e: # Catch any other potential errors during loading
            print(f"[SimpleChestShop] Error loading config.yml: {e}")
            print("[SimpleChestShop] Using default configuration.")
            config = default_config # Fallback to default config on error

    # After loading (or creating) config, merge defaults to ensure all settings exist
    config = {**default_config, **(config or {})} # Merge defaults with loaded config, prioritizing loaded values

    print("[SimpleChestShop] Configuration loaded.") # Indicate config loading is complete
    if config.get("settings", {}).get("debug_mode", False): # Example of using debug_mode from config
        print("[SimpleChestShop] Debug mode is enabled.")

# --- Helper Functions ---

def is_in_town(location):
    """Checks if the location is within a town."""
    try:
        return TownyUniverse.getInstance().getTownBlock(location).hasTown() # Use hasTown() instead of is not None
    except:
        return False



# --- Event Handlers ---

@event("block.SignChangeEvent")
def on_sign_change(event):
    player = event.getPlayer()
    lines = event.getLines()
    location = event.getBlock().getLocation()

    if lines[0].lower() == "[shop]":
        if config.get("permissions", {}).get("enable_permissions", True): # Check if permission checks are enabled
            create_perm = config.get("permissions", {}).get("create_shop_permission", "chestshop.create") # Get permission node from config
            if not player.hasPermission(create_perm): # Check if player has the create shop permission
                message = config.get("messages", {}).get("no_shop_permission", "§c[Shop] System: You do not have permission to create shops.")
                player.sendMessage(message)
                event.setCancelled(True) # Cancel sign creation
                return # Stop processing

        if not config.get("towny", {}).get("enable_towny_integration", True):
            pass
        elif config.get("towny", {}).get("require_town", False):
            if not is_in_town(location):
                message = config.get("messages", {}).get("shop_must_be_in_town", "§c[Shop] System: Shops can only be created within town boundaries.")
                player.sendMessage(message)
                event.setCancelled(True)
                return

        if config.get("settings", {}).get("enable_shop_creation", True):
            message = config.get("messages", {}).get("shop_detected", "§aShop sign detected!")
            player.sendMessage(message)
        else:
            player.sendMessage("§c[Shop] System: Shop creation is currently disabled by the server.")
            event.setCancelled(True)

@event("player.PlayerInteractEvent")
def on_player_interact(event):
    # This function will be called when a player interacts with something
    if event.getAction() == Action.RIGHT_CLICK_BLOCK: # Check if it's a right-click on a block
        block = event.getClickedBlock()
        if block.getType() == Material.CHEST: # Check if the block is a chest
            player = event.getPlayer()
            player.sendMessage("§bChest right-clicked!") # Send a message to the player

# --- Plugin Class ---

@plugin("SimpleChestShop") # This name will be used to identify your plugin
class SimpleChestShopPlugin:
    def on_enable(self):
        load_config() # Load the configuration when the plugin starts
        print("[SimpleChestShop] Plugin enabled!")

    def on_disable(self):
        print("[SimpleChestShop] Plugin disabled!")