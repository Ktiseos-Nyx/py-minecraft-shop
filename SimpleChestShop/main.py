# -*- coding: utf-8 -*-
"""
SimpleChestShop - A PySpigot plugin for creating simple chest shops in Minecraft.

This plugin allows players to create chest shops by placing signs on chests,
enabling item trading with other players using server currency (via Vault).
Integrates with TownyAdvanced for town-based shop restrictions and LuckPerms
for permission control.
"""
import os  # Standard library imports FIRST

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
# We now remove the config loading, so all are hard coded.
VAULT_ENABLED = True  # Global flag to track if Vault is enabled (RENAMED to UPPER_CASE)
VAULT_ECONOMY = None   # Global variable to store the Vault Economy service (RENAMED to UPPER_CASE)
ENABLE_SHOP_CREATION = True
DEBUG_MODE = False
SHOP_DETECTED_MESSAGE = "§a[Shop] System: Shop sign detected and enabled!"
NO_SHOP_PERMISSION_MESSAGE = "§c[Shop] System: You do not have permission to create shops."
SHOP_MUST_BE_IN_TOWN_MESSAGE = "§c[Shop] System: Shops can only be created within town boundaries."
ENABLE_TOWNY_INTEGRATION = True
REQUIRE_TOWN = False
ENABLE_PERMISSIONS = True
CREATE_SHOP_PERMISSION = "chestshop.create"
CURRENCY_SYMBOL = "$"
SHOP_BOUGHT_ITEM = "§a[Shop] System: You bought {quantity} {item_name} for {price}."
SHOP_SOLD_ITEM = "§a[Shop] System: You sold {quantity} {item_name} for {price}."
SHOP_NO_MONEY = "§c[Shop] System: You do not have enough money to do that!"
SHOP_NO_ITEMS = "§c[Shop] System: You do not have the required items for that!"

def get_vault_economy():
    """Retrieves the Vault economy service."""
    global VAULT_ECONOMY, VAULT_ENABLED

    if not VAULT_ENABLED:
        print "[SimpleChestShop] Vault integration is disabled in config." # Python 2.7 print statement (no parentheses)
        return None  # Vault integration disabled

    if server.getPluginManager().getPlugin("Vault") is None:
        print "[SimpleChestShop] Vault plugin not found! Disabling Vault integration." # Python 2.7 print statement (no parentheses)
        VAULT_ENABLED = False
        return None  # Vault not found

    rsp = server.getServicesManager().getRegistration(Economy)

    if rsp is None:
        print "[SimpleChestShop] Vault Economy service not found! Disabling Vault integration." # Python 2.7 print statement (no parentheses)
        VAULT_ENABLED = False
        return None  # Economy service not found

    VAULT_ECONOMY = rsp.getProvider()
    if VAULT_ECONOMY is not None:
        VAULT_ENABLED = True
        print "[SimpleChestShop] Vault integration enabled. Economy provider: {}".format(VAULT_ECONOMY.getName()) # Python 2.7 print statement (no parentheses)
        return VAULT_ECONOMY

    # No 'else' needed here!  If we reach this point, it means the 'if' condition was false.
    print "[SimpleChestShop] Failed to get Vault Economy provider! Disabling Vault integration." # Python 2.7 print statement (no parentheses)
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
        if ENABLE_PERMISSIONS:  # Check if permission checks are enabled
            create_perm = CREATE_SHOP_PERMISSION  # Get permission node from config
            if not player.hasPermission(create_perm):  # Check if player has the create shop permission
                print NO_SHOP_PERMISSION_MESSAGE  # Python 2.7 print statement (no parentheses)
                player.sendMessage(NO_SHOP_PERMISSION_MESSAGE)
                event.setCancelled(True)  # Cancel sign creation
                return  # Stop processing

        if not ENABLE_TOWNY_INTEGRATION:
            pass
        elif REQUIRE_TOWN:
            if not is_in_town(location):  # Corrected indentation - Removed extra indentation
                message = SHOP_MUST_BE_IN_TOWN_MESSAGE  # Get the message.
                player.sendMessage(message)
                event.setCancelled(True)
                return

        if ENABLE_SHOP_CREATION:  # Check if shop creation is enabled in general
            player.sendMessage(SHOP_DETECTED_MESSAGE)
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
        print "[SimpleChestShop] Plugin enabled!"  # Python 2.7 print statement (no parentheses)
        get_vault_economy()  # Call get_vault_economy() on plugin enable to detect and get Vault

    def on_disable(self):
        """Called when the plugin is disabled."""
        print "[SimpleChestShop] Plugin disabled!"  # Python 2.7 print statement (no parentheses)
