# -*- coding: utf-8 -*-
"""
SimpleChestShop - A PySpigot plugin for creating simple chest shops in Minecraft.

This plugin allows players to create chest shops by placing signs on chests,
enabling item trading with other players using server currency (via Vault).
Integrates with TownyAdvanced for town-based shop restrictions and LuckPerms
for permission control.
"""
import os  # Standard library imports FIRST
import pyspigot as ps  # Correct pyspigot import

# Vault Imports (for Vault API)
from net.milkbowl.vault.economy import Economy
from com.palmergames.bukkit.towny import TownyUniverse

#org bukkit imports
from org.bukkit.plugin.java import JavaPlugin
from org.bukkit.event.Listener import Listener
from org.bukkit.event.player import PlayerInteractEvent
from org.bukkit.event.block import BlockBreakEvent
from org.bukkit.Material import Material
from org.bukkit.block import Block
from org.bukkit.entity import Player
from org.bukkit.inventory import ItemStack
from org.bukkit.inventory.meta import ItemMeta
from org.bukkit.ChatColor import ChatColor
from org.bukkit import Location
from org.bukkit.block import Sign # Import Sign for future sign detection

import ruamel.yaml as yaml # Make sure ruamel.yaml is installed correctly in python-libs

CONFIG_FILE = "config.yml" # Name of the configuration file
SHOP_CHEST_MATERIAL_CONFIG_KEY = "shop_chest_material" # Key in config.yml for shop chest material
SHOP_IDENTIFIER_SIGN_TEXT_CONFIG_KEY = "shop_identifier_sign_text" # Key for shop sign text
DEFAULT_SHOP_CHEST_MATERIAL = Material.CHEST # Default material if not in config
DEFAULT_SHOP_IDENTIFIER_SIGN_TEXT = "[Shop]" # Default sign text if not in config

class ChestShop(JavaPlugin, Listener):

    def onEnable(self):
        self.load_plugin_config() # Load configuration from config.yml
        self.getServer().getPluginManager().registerEvents(self, self)
        self.getLogger().info("SimpleChestShop plugin enabled!")
        self.shop_locations = set() # Placeholder: Keep track of shop chest locations (not persistent yet)
        self.load_shop_locations() # Placeholder: Load saved shop locations (not implemented yet)

    def onDisable(self):
        self.save_shop_locations() # Placeholder: Save shop locations (not implemented yet)
        self.getLogger().info("SimpleChestShop plugin disabled!")

    def load_plugin_config(self):
        """Loads the plugin configuration from config.yml using ruamel.yaml."""
        config_path = self.getDataFolder().getAbsolutePath() + "/" + CONFIG_FILE
        try:
            with open(config_path, 'r') as f:
                config = yaml.YAML().load(f)
                if not config:
                    config = {} # Handle empty config file
        except IOError:
            config = {} # Default to empty config if file not found

        # Load shop chest material from config, or use default
        material_name = config.get(SHOP_CHEST_MATERIAL_CONFIG_KEY, DEFAULT_SHOP_CHEST_MATERIAL.name())
        try:
            self.shop_chest_material = Material.valueOf(material_name.upper()) # Convert config string to Material
        except ValueError:
            self.shop_chest_material = DEFAULT_SHOP_CHEST_MATERIAL # Fallback to default if invalid material name in config
            self.getLogger().warning("Invalid shop_chest_material in config: '{}'. Using default: '{}'.".format(material_name, DEFAULT_SHOP_CHEST_MATERIAL.name()))

        # Load shop identifier sign text from config, or use default
        self.shop_identifier_sign_text = config.get(SHOP_IDENTIFIER_SIGN_TEXT_CONFIG_KEY, DEFAULT_SHOP_IDENTIFIER_SIGN_TEXT)

        self.config = config # Store the loaded config for potential future use (saving, etc.)
        self.getLogger().info("Configuration loaded from '{}'".format(CONFIG_FILE))
        self.getLogger().info("Shop chest material: '{}'".format(self.shop_chest_material.name()))
        self.getLogger().info("Shop identifier sign text: '{}'".format(self.shop_identifier_sign_text))


    def save_config(self): # Method to save config (not currently used, but good to have)
        """Saves the current configuration to config.yml."""
        config_path = self.getDataFolder().getAbsolutePath() + "/" + CONFIG_FILE
        with open(config_path, 'w') as f:
            yaml.YAML().dump(self.config, f)
        self.getLogger().info("Configuration saved to '{}'".format(CONFIG_FILE))


    def load_shop_locations(self):
        """Placeholder: Loads shop locations from persistent storage (not implemented yet)."""
        # --- In a real plugin, you would load shop locations from config or a data file here ---
        self.shop_locations = set() # Initialize as empty for now
        self.getLogger().info("Shop locations loaded (placeholder - not persistent).")

    def save_shop_locations(self):
        """Placeholder: Saves shop locations to persistent storage (not implemented yet)."""
        # --- In a real plugin, you would save shop locations to config or a data file here ---
        self.getLogger().info("Shop locations saved (placeholder - not persistent).")

    def is_shop_chest(self, block):
        """
        Checks if a given block is a shop chest.
        Currently, this is a placeholder and simply checks if the block's material matches the configured shop chest material.
        In a real implementation, you would check for an attached sign with the shop identifier text,
        or use other methods to identify shop chests.
        """
        if block.getType() == self.shop_chest_material:
            # --- Future: Check for a sign attached to the chest with self.shop_identifier_sign_text ---
            # --- Sign checking logic would go here (more complex, not implemented in this basic example) ---
            # --- For now, assume any chest of the configured material is a shop chest (for basic testing) ---
            return True
        return False

    def onPlayerInteract(self, event):
        """Handles player interactions with blocks (especially chests)."""
        action = event.getAction()
        block = event.getClickedBlock()
        player = event.getPlayer()

        if action == PlayerInteractEvent.Action.RIGHT_CLICK_BLOCK and block.getType() == self.shop_chest_material:
            if self.is_shop_chest(block):
                self.handle_shop_interaction(player, block) # Handle right-click interaction with a shop chest
            else:
                player.sendMessage(ChatColor.GRAY + "This is just a regular {}.".format(self.shop_chest_material.name().lower().replace('_', ' '))) # Indicate it's a regular chest

        elif action == PlayerInteractEvent.Action.LEFT_CLICK_BLOCK and block.getType() == self.shop_chest_material:
            if self.is_shop_chest(block):
                self.handle_shop_break_attempt(player, block) # Handle left-click attempt to break a shop chest
            else:
                player.sendMessage(ChatColor.GRAY + "You left-clicked a regular {}.".format(self.shop_chest_material.name().lower().replace('_', ' '))) # Indicate it's a regular chest

    def handle_shop_interaction(self, player, chest_block):
        """Placeholder: Handles player interaction (right-click) with a shop chest."""
        location = chest_block.getLocation()
        player.sendMessage(ChatColor.GREEN + "Shop Interaction with chest at: " + str(location.getBlockX()) + ", " + str(location.getBlockY()) + ", " + str(location.getBlockZ()))
        player.sendMessage(ChatColor.YELLOW + "Shop interface would open here in a real chest shop plugin.")
        # --- Implement shop interface (inventory GUI, item display, buying/selling) here ---

    def handle_shop_break_attempt(self, player, chest_block):
        """Handles player attempts to break a shop chest (left-click). Prevents breaking."""
        player.sendMessage(ChatColor.RED + ChatColor.BOLD + "You cannot break shop chests directly!")
        player.sendMessage(ChatColor.RESET + ChatColor.GRAY + "Interact (right-click) to use the shop.")
        # Breaking is prevented in the onBlockBreak event listener

    def onBlockBreak(self, event):
        """Listener for BlockBreakEvent. Prevents breaking of shop chests."""
        block = event.getBlock()
        player = event.getPlayer()
        if block.getType() == self.shop_chest_material:
            if self.is_shop_chest(block):
                event.setCancelled(True) # Prevent breaking shop chests
                player.sendMessage(ChatColor.RED + ChatColor.BOLD + "You cannot break shop chests!")
                player.sendMessage(ChatColor.RESET + ChatColor.GRAY + "Use /removeshop to remove a shop (command not yet implemented).") # Suggest shop removal command (future feature)
            # else:  No message for breaking regular chests in onBlockBreak - let default behavior happen


# --- Further Steps to Develop a Real Chest Shop Plugin (Beyond Basic Fixes - Reminder) ---
# 1. Shop Identification: Implement robust shop chest identification (e.g., signs, metadata).
# 2. Shop Creation:  Commands or methods for players to create shops (set buy/sell items, prices).
# 3. Shop Data Storage: Store shop information (location, items, prices) persistently (config file, database).
# 4. Shop Inventory GUI: Create a user-friendly inventory interface for buying/selling.
# 5. Transaction Handling: Implement secure and reliable item and currency transactions.
# 6. Permissions: Add permissions for shop creation, usage, admin commands.
# 7. Configuration: Make various aspects configurable (shop material, sign text, prices, etc.) - basic config loading is now in place.
# 8. Error Handling and Edge Cases:  Handle potential errors gracefully (e.g., insufficient funds, invalid items).
# 9. Security:  Consider security aspects (preventing exploits, griefing).
# 10. Testing and Refinement: Thoroughly test the plugin and refine features based on testing and feedback.
