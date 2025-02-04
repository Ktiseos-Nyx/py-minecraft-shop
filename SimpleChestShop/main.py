# coding=utf-8
import os  # Standard library imports FIRST
import pyspigot as ps  # Correct pyspigot import

# Third-party plugin API imports (Vault, Towny)
from net.milkbowl.vault2.economy import Economy  # CORRECT Vault import (note 'vault2')
from com.palmergames.bukkit.towny import TownyUniverse # Towny API


from org.bukkit import Listener
from org.bukkit import EventHandler
from org.bukkit import PlayerInteractEvent
from org.bukkit import BlockBreakEvent
from org.bukkit import Material
from org.bukkit import Block
from org.bukkit import Player
from org.bukkit import ItemStack
from org.bukkit import ItemMeta
from org.bukkit import ChatColor
from org.bukkit import Location
from org.bukkit import Sign
from org.bukkit import Command # Import Command and CommandSender for command handling
from org.bukkit import CommandSender

# I'll work on the YAML soon, the reason for the "DELETE" the classes is sometihng something: Since in java Material is directly a class not a file (unlike python) - So i'm assuming this is the same for the rest of them.
#Yaml Config
import ruamel.yaml as yaml

CONFIG_FILE = "config.yml"
SHOP_CHEST_MATERIAL_CONFIG_KEY = "shop_chest_material"
SHOP_IDENTIFIER_SIGN_TEXT_CONFIG_KEY = "shop_identifier_sign_text"
DEFAULT_SHOP_CHEST_MATERIAL = Material.CHEST
DEFAULT_SHOP_IDENTIFIER_SIGN_TEXT = "[Shop]"

class ChestShop(JavaPlugin, Listener):

    def onEnable(self):
        self.load_plugin_config()
        self.getServer().getPluginManager().registerEvents(self, self)
        self.getLogger().info("SimpleChestShop plugin enabled!")
        self.shop_locations = set() # Placeholder: Keep track of shop chest locations (not persistent yet)
        self.load_shop_locations() # Placeholder: Load saved shop locations (not implemented yet)

        # --- Vault Economy Setup (Placeholder - Basic Initialization) ---
        self.economy = self.setup_economy() # Try to setup Vault economy
        if self.economy:
            self.getLogger().info("Vault economy integration enabled (placeholder - not fully functional yet).")
        else:
            self.getLogger().warning("Vault economy provider not found. Economy features will be disabled.")


    def onDisable(self):
        self.save_shop_locations()
        self.getLogger().info("SimpleChestShop plugin disabled!")

    def load_plugin_config(self):
        config_path = self.getDataFolder().getAbsolutePath() + "/" + CONFIG_FILE
        try:
            with open(config_path, 'r') as f:
                config = yaml.YAML().load(f)
                if not config:
                    config = {}
        except IOError:
            config = {}

        material_name = config.get(SHOP_CHEST_MATERIAL_CONFIG_KEY, DEFAULT_SHOP_CHEST_MATERIAL.name())
        try:
            self.shop_chest_material = Material.valueOf(material_name.upper())
        except ValueError:
            self.shop_chest_material = DEFAULT_SHOP_CHEST_MATERIAL
            self.getLogger().warning("Invalid shop_chest_material in config: '{}'. Using default: '{}'.".format(material_name, DEFAULT_SHOP_CHEST_MATERIAL.name()))

        self.shop_identifier_sign_text = config.get(SHOP_IDENTIFIER_SIGN_TEXT_CONFIG_KEY, DEFAULT_SHOP_IDENTIFIER_SIGN_TEXT)

        self.config = config
        self.getLogger().info("Configuration loaded from '{}'".format(CONFIG_FILE))
        self.getLogger().info("Shop chest material: '{}'".format(self.shop_chest_material.name()))
        self.getLogger().info("Shop identifier sign text: '{}'".format(self.shop_identifier_sign_text))


    def save_config(self):
        config_path = self.getDataFolder().getAbsolutePath() + "/" + CONFIG_FILE
        with open(config_path, 'w') as f:
            yaml.YAML().dump(self.config, f)
        self.getLogger().info("Configuration saved to '{}'".format(CONFIG_FILE))


    def load_shop_locations(self):
        self.shop_locations = set()
        self.getLogger().info("Shop locations loaded (placeholder - not persistent).")

    def save_shop_locations(self):
        self.getLogger().info("Shop locations saved (placeholder - not persistent).")

    def is_shop_chest(self, block):
        if block.getType() == self.shop_chest_material:
            return True
        return False

    @EventHandler
    def onPlayerInteract(self, event):
        action = event.getAction()
        block = event.getClickedBlock()
        player = event.getPlayer()

        if action == PlayerInteractEvent.Action.RIGHT_CLICK_BLOCK and block.getType() == self.shop_chest_material:
            if self.is_shop_chest(block):
                self.handle_shop_interaction(player, block)
            else:
                player.sendMessage(ChatColor.GRAY + "This is just a regular {}.".format(self.shop_chest_material.name().lower().replace('_', ' ')))

        elif action == PlayerInteractEvent.Action.LEFT_CLICK_BLOCK and block.getType() == self.shop_chest_material:
            if self.is_shop_chest(block):
                self.handle_shop_break_attempt(player, block)
            else:
                player.sendMessage(ChatColor.GRAY + "You left-clicked a regular {}.".format(self.shop_chest_material.name().lower().replace('_', ' ')))

    def handle_shop_interaction(self, player, chest_block):
        location = chest_block.getLocation()
        player.sendMessage(ChatColor.GREEN + "Shop Interaction with chest at: " + str(location.getBlockX()) + ", " + str(location.getBlockY()) + ", " + str(location.getBlockZ()))
        player.sendMessage(ChatColor.YELLOW + "Shop interface would open here in a real chest shop plugin.")
        # --- Future: Implement shop interface (inventory GUI, item display, buying/selling) and Vault economy transactions here ---

    def handle_shop_break_attempt(self, player, chest_block):
        player.sendMessage(ChatColor.RED + ChatColor.BOLD + "You cannot break shop chests directly!")
        player.sendMessage(ChatColor.RESET + ChatColor.GRAY + "Interact (right-click) to use the shop.")

    @EventHandler
    def onBlockBreak(self, event):
        block = event.getBlock()
        player = event.getPlayer()
        if block.getType() == self.shop_chest_material:
            if self.is_shop_chest(block):
                event.setCancelled(True)
                player.sendMessage(ChatColor.RED + ChatColor.BOLD + "You cannot break shop chests!")
                player.sendMessage(ChatColor.RESET + ChatColor.GRAY + "Use /removeshop to remove a shop (command not yet implemented).")


    # --- Vault Economy Setup (Placeholder Function) ---
    def setup_economy(self):
        """Sets up Vault economy integration if Vault is available."""
        if self.getServer().getPluginManager().getPlugin("Vault") == None:
            return False
        rsp = self.getServer().getServicesManager().getRegistration(Economy.class)
        if rsp == None:
            return False
        self.getLogger().info("Vault Economy service found: {}".format(rsp.getProvider().getName())) # Log Vault provider
        return rsp.getProvider()


    # --- Command Handling for /removeshop ---
    def onCommand(self, sender, command, label, args):
        if command.getName().lower() == "removeshop":
            return self.handle_removeshop_command(sender, args) # Call handler for /removeshop command
        return False # Return false if command is not handled


    def handle_removeshop_command(self, sender, args):
        """Handles the /removeshop command."""
        if not isinstance(sender, Player): # Command can only be used by players
            sender.sendMessage(ChatColor.RED + "This command can only be used by players in-game.")
            return True

        player = sender
        target_block = player.getTargetBlock(None, 5) # Get block player is looking at within 5 blocks range

        if not target_block or target_block.getType() != self.shop_chest_material:
            player.sendMessage(ChatColor.RED + "You must be looking at a shop chest to use /removeshop.")
            return True

        location = target_block.getLocation()
        if location in self.shop_locations: # Check if it's registered as a shop (using placeholder shop_locations set)
            self.shop_locations.remove(location) # Remove from shop locations (placeholder removal)
            player.sendMessage(ChatColor.GREEN + "Shop removed at location: " + str(location.getBlockX()) + ", " + str(location.getBlockY()) + ", " + str(location.getBlockZ()))
            # --- Future: Implement persistent removal of shop data (from config/data file) ---
            # --- Future: Potentially refund items/money to shop owner if needed ---
        else:
            player.sendMessage(ChatColor.YELLOW + "The block you are looking at is not registered as a shop.")

        return True # Command handled successfully
