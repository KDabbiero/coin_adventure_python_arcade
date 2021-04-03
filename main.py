# Create a game using the Tiled application. Get more practice using Sprites. Have a games with levels. Also have the game perform a scrolling view.

import arcade
import random
import math
import arcade.gui
from arcade.gui import UIManager
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

CHARACTER_SCALING = .4
TILE_SCALING = 0.5
NUM_SCALING = 0.5
SPRITE_SCALING = 0.4
# Globals for the bullet.
SPRITE_SCALING_BULLET = 0.5
BULLET_SPEED = 5

# Globals for the coins.
SPRITE_SCALING_COIN = 0.2
NUMBER_OF_COINS = 5
MOVEMENT_SPEED = 5

# Movement speed of player in pixels per frame.
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = .6
PLAYER_JUMP_SPEED = 10

# Used to resize the window.
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Coin Adventure"

# How many pixels to keep as a minimum margin between the character and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 100
TOP_VIEWPORT_MARGIN = 100

# Create the player sprite class.
class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = SPRITE_SCALING
        self.lives = 3
        self.textures = []

        # Load a texture for the sprite. Right facing.
        texture1 = arcade.load_texture(r'female_walk1.png')
        self.textures.append(texture1)

        # Left facing.
        texture2 = arcade.load_texture(r'female_walk1.png', flipped_horizontally=True)
        self.textures.append(texture2)

        # By default face to the right.
        self.texture = self.textures[0]

# Create the Menu View.
class MenuView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLUE_GRAY)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Coin Adventure", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.BLACK, font_size=20, anchor_x="center")
        arcade.draw_text("Click to continue to Instructions", SCREEN_WIDTH/2, SCREEN_HEIGHT/3, arcade.color.BLACK, font_size=15, anchor_x="center")
    
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        instructions_view = InstructionView()
        self.window.show_view(instructions_view)

# Create the Instruction View.
class InstructionView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLUSH)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Instructions", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.BLACK, font_size=50, anchor_x="center")
        arcade.draw_text("Left Arrow: Move Left", SCREEN_WIDTH/2, SCREEN_HEIGHT/4, arcade.color.BLACK, font_size=20, anchor_x="center")
        arcade.draw_text("Right Arrow: Move Right", SCREEN_WIDTH/2, SCREEN_HEIGHT/5, arcade.color.BLACK, font_size=20, anchor_x="center")
        arcade.draw_text("Up Arrow: Jump", SCREEN_WIDTH/2, SCREEN_HEIGHT/7, arcade.color.BLACK, font_size=20, anchor_x="center")
        arcade.draw_text("Mouse Click: Shoot Laser", SCREEN_WIDTH/2, SCREEN_HEIGHT/12, arcade.color.BLACK, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)

class GameView(arcade.View):
    def __init__(self):
        # For the Game view to work.
        super().__init__()

        self.time_taken = 0

        # Initialize the physics engine.
        self.physics_engine = None

        # For the tiles.
        self.tile_list = arcade.SpriteList()

        # Load in the map.tmx file from the tiled editor.
        map_name = "map.tmx"

        # Read in the tiled map.
        my_map = arcade.tilemap.read_tmx(map_name)

        # Load the tiles.
        self.tile_list = arcade.tilemap.process_layer(map_object=my_map, layer_name="Platforms", scaling=TILE_SCALING, use_spatial_hash=True) 

        # For the bullets.
        self.bullet_list = arcade.SpriteList()

        # For the player Sprite.
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player()
        self.player_sprite.center_x = 256
        self.player_sprite.center_y = 256
        self.player_list.append(self.player_sprite)

        # For the coins.
        self.coin_list = arcade.SpriteList()
                # Draw the coins in the proper places.
        for i in range(NUMBER_OF_COINS):
            # Create the coin instance.
            coin = arcade.Sprite(r'coinGold.png', SPRITE_SCALING_COIN, hit_box_detail=4.5)

            # Boolean variable if we successfully place the coin.
            coin_placed_successfully = False

            # Keep trying until the coin is placed successfully.
            while not coin_placed_successfully:
                # Position the coin.
                coin.center_x = random.randrange(SCREEN_WIDTH)
                coin.center_y = random.randrange(300, SCREEN_HEIGHT)

                # See if the coin is hitting a wall.
                tile_hit_list = arcade.check_for_collision_with_list(coin, self.tile_list)

                # See if the coin is hitting another coin.
                coin_hit_list = arcade.check_for_collision_with_list(coin, self.coin_list)

                if len(tile_hit_list) == 0 and len(coin_hit_list) == 0:
                    # Coin is successfully placed.
                    coin_placed_successfully = True
            
            # Add the coin to the lists.
            self.coin_list.append(coin)

        # Load the jump sound when the player jumps.
        self.jump_sound = arcade.load_sound(':resources:sounds/jump1.wav')
        # Load the sound for the gun shot.
        self.gun_shot = arcade.sound.load_sound(":resources:sounds/laser1.wav")
        # Load the sound for the bullet hitting the coins.
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/phaseJump1.wav")

        # Used to keep track of the scrolling.
        self.view_bottom = 0
        self.view_left = 0

        # Create the physics engine.
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.tile_list, GRAVITY)

        # Initialize the score
        self.score = 0

    # Function for the view to work.
    def on_show(self):
        arcade.set_background_color(arcade.color.BOTTLE_GREEN)

    def on_draw(self):
        # Clear the screen to the background color.
        arcade.start_render()

        # Draw the tile sprites.
        self.tile_list.draw()

        # Draw the player sprite.
        self.player_list.draw()

        # Draw the bullets sprites.
        self.bullet_list.draw()

        # Actually draw the coin list.
        self.coin_list.draw()

        # Draw the lives of the player sprite.
        lives_text = f'Lives: {self.player_sprite.lives}'
        arcade.draw_text(lives_text, 10, 30, arcade.color.BLACK, 14)

        # Draw the score.
        score_text = f'Score: {self.score}'
        arcade.draw_text(score_text, SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, arcade.color.BLACK, 14)

    # Generates our bullets.
    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked."""
        # Create a bullet.
        bullet = arcade.Sprite(r'laserRedHorizontal.png', SPRITE_SCALING_BULLET)

        # Callibrate the bullet to be at the players position.
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # Get from the mouse the destination location for the bullet. 
        dest_x = x + self.view_left
        dest_y = y + self.view_bottom

        # Do math to calculate how to get the bullet to the destination. Calculate the angle in radians between the start points and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the bullet sprite so it doesn't look like it is flying sideways.
        bullet.angle = math.degrees(angle)
        print(f'Bullet angle: {bullet.angle:.2f}')

        # Taking into account the angle, calculate our change_x and change_y. Use an if statement to apply the velocity for when the player_sprite is facing left (self.player_sprite.textures[1]) or facing right (self.player_sprite.textures[0]).
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        # Add the bullet to the appropriate list.
        self.bullet_list.append(bullet)

    def on_key_press(self, key, modifiers):
        """ Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                #Play the jump sound.
                #arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.player_sprite.texture = self.player_sprite.textures[1]
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.player_sprite.texture = self.player_sprite.textures[0]

    def on_key_release(self, key, modifiers):
        """ Called whenever a user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic"""
        self.window.time_taken += delta_time

        # Call update on all sprites.
        self.player_sprite.update()
        self.coin_list.update()
        self.bullet_list.update()

        # Ensures that the bullet dies when it hits a tile.
        for bullet in self.bullet_list:
            bullet_tile_hit_list = arcade.check_for_collision_with_list(bullet, self.tile_list)
            if len(bullet_tile_hit_list) > 0:
                bullet.remove_from_sprite_lists()

        # Loop through each bullet.
        for bullet in self.bullet_list:
            # Check this bullet to see if it hit a coin.
            bullet_hit_list = arcade.check_for_collision_with_list(bullet, self.coin_list)
            # If it did, get rid of the bullet.
            if len(bullet_hit_list) > 0:
                bullet.remove_from_sprite_lists()
            # For every coin we hit, add to the score and remove the coin.
            for coin in bullet_hit_list:
                coin.kill()
                self.score += 1
                self.window.total_score += 1
            # If the bullet flies off-screen, remove it.
            if bullet.bottom > SCREEN_WIDTH or bullet.top < 0 or bullet.right < 0 or bullet.left > SCREEN_WIDTH:
                bullet.remove_from_sprite_lists()

        #if len(self.coin_list) == 0:
            #get_user_info_for_LB = GetUserInfoForLB()
            #get_user_info_for_LB.time_taken = self.time_taken
            #self.window.show_view(get_user_info_for_LB)

        # Determine when the player losses their life and reset them to where they started.
        if self.player_sprite.center_y < 127:
            self.player_sprite.center_x = 256
            self.player_sprite.center_y = 256
            self.player_sprite.lives -= 1

        # Move the playeyr with the physics engine.
        self.physics_engine.update()
    
        # Manage the scrolling of the viewport.
        changed = False

        # Scroll left.
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right.
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up.
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down.
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integer values or else we end up with pixels that don't line up on the screen.
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Perform the scrolling operation.
            arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

        # When the player runs out of lives a game over screen is displayed.
        if self.player_sprite.lives == 0:
            game_over_view = GameOverView()
            self.window.show_view(game_over_view)

class LeaderboardView(arcade.View):
    def __init__(self):
        super().__init__()

        # List for the top leaders from the leaderboard.txt file.
        self.leaders_list = []

    def on_show(self):
        self.window.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        arcade.set_background_color(arcade.color.DEEP_RUBY)

    def on_draw(self):
        arcade.start_render()

        arcade.draw_text("Press the SPACE bar to continue to your game summary.", SCREEN_WIDTH/2, SCREEN_HEIGHT/8, arcade.color.WHITE)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_over_view = GameOverView()
            self.window.show_view(game_over_view)

# Create the Game Over View.
class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.BOTTLE_GREEN)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        arcade.start_render()

        """Draw "Game Over" across the screen."""
        arcade.draw_text("Game Over", 100, SCREEN_HEIGHT/2, arcade.color.WHITE, 54)

        arcade.draw_text("Click to restart", 162, SCREEN_HEIGHT/ 3, arcade.color.WHITE, 24)

        time_taken_formatted = f"{round(self.window.time_taken, 2)} seconds"
        arcade.draw_text(f"Time taken: {time_taken_formatted}", SCREEN_WIDTH / 2,SCREEN_HEIGHT/4,  arcade.color.GRAY, font_size=15, anchor_x="center")

        output_total = f"Total Score: {self.window.total_score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.total_score = 0
    window.time_taken = 0
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()