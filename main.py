import pygame
import time
from random import randint as r

class Coin:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx   # direction on the x axis
        self.vy = vy   # direction on the y axis

class RoboCoin():
    def __init__(self):
        pygame.init()
        self.width = 1.3 * 640
        self.height = 1.3 * 480
        self.window = pygame.display.set_mode((self.width, self.height))
        self.load_images()

        # robot coordinates, directions, speed
        self.robot_x = 400
        self.robot_y = 400
        self.to_left = False
        self.to_right = False
        self.to_up = False
        self.to_down = False
        self.robot_movement_speed = 3

        # monster: starting point is always at (0,0)
        self.set_monster_to_origo()
        self.monster_movement_speed = 0.5

        # coin size, coordinates and movement speed & direction
        self.coin_list = []  # max 10 coins can be on the list/screen
        self.coin_size = self.coin.get_width()
        self.coin_center = int(self.coin_size / 2)
        self.create_first_coins()
        self.points = 0
        self.lives = 2  # monster-robot contact will deduct 1 life, 3 contacts will end the game
        
        pygame.display.set_caption("RoboCoin")
        self.game_font = pygame.font.SysFont("Arial", 22)
        self.end_of_game = False
        self.clock = pygame.time.Clock()
        
        self.welcome_window()
        self.main_loop()

    def welcome_window(self):
        self.window.fill((150,150,150))
        coin_text = "Collect as many coins as you can."
        avoid_monster_text = "Avoid the monster. You have 3 lives."
        self.window.blit(self.game_font.render(coin_text, True, (255, 0, 0)), (250, 250))
        self.window.blit(self.game_font.render(avoid_monster_text, True, (255, 0, 0)), (250, 280))
        pygame.display.flip()
        time.sleep(5)   # window is visible for 5 seconds and then the game starts

    def load_images(self):
        self.robot = pygame.image.load("robot.png")
        self.monster = pygame.image.load("monster.png")
        self.coin = pygame.image.load("coin.png")
    
    def set_monster_to_origo(self):
        self.monster_x = 0
        self.monster_y = 0
    
    def create_first_coins(self):  # creating the first 10 coins, used only once during the game
        for i in range(0,10):
            new_coin = Coin(r(0, self.width-self.coin_size), r(0, self.height-self.coin_size), 3, 3)
            self.coin_list.append(new_coin)
    
    def coin_new_coordinates(self):  # creating new coins during the game
        return (r(0, self.width-self.coin_size), r(0, self.height-self.coin_size))

    def robot_move(self):
        if self.to_left == True and self.robot_x >= 0:
            self.robot_x -= self.robot_movement_speed
        if self.to_right == True and self.robot_x + self.robot.get_width() <= self.width:
            self.robot_x += self.robot_movement_speed
        if self.to_up == True and self.robot_y >= 0:
            self.robot_y -= self.robot_movement_speed
        if self.to_down == True and self.robot_y + self.robot.get_height() <= self.height:
            self.robot_y += self.robot_movement_speed
    
    def monster_movement(self):
        if self.monster_x > self.robot_x: self.monster_x -= self.monster_movement_speed
        if self.monster_x < self.robot_x: self.monster_x += self.monster_movement_speed
        if self.monster_y > self.robot_y: self.monster_y -= self.monster_movement_speed
        if self.monster_y < self.robot_y: self.monster_y += self.monster_movement_speed
    
    def coin_movement(self):
        for coin in self.coin_list:
            coin.x += coin.vx
            coin.y += coin.vy
            if coin.vx > 0 and coin.x + self.coin_size >= self.width: coin.vx = -coin.vx
            if coin.vy > 0 and coin.y + self.coin_size >= self.height: coin.vy = -coin.vy
            if coin.vx < 0 and coin.x <= 0: coin.vx = -coin.vx
            if coin.vy < 0 and coin.y <= 0: coin.vy = -coin.vy
    
    def robot_monster_collision_check(self):  # using shorter coordinates
        #rlx = robot left x, rrx = robot right x
        rlx = self.robot_x; rrx = self.robot_x + self.robot.get_width()
        # ruy = robot upper y, rdy = robot down y
        ruy = self.robot_y; rdy = self.robot_y + self.robot.get_height()
        # the same for robot
        mlx = self.monster_x + 20; mrx = self.monster_x + self.monster.get_width() - 20
        muy = self.monster_y + 20; mdy = self.monster_y + self.monster.get_height() - 20
        if (rlx < mlx and mlx < rrx) and (ruy < muy and muy < rdy):
                self.robot_and_monster_collided(); time.sleep(1)
        elif (rlx < mlx and mlx < rrx) and (ruy < mdy and mdy < rdy):
                self.robot_and_monster_collided(); time.sleep(1)
        elif (rlx < mrx and mrx < rrx) and (ruy < muy and muy < rdy):
                self.robot_and_monster_collided(); time.sleep(1)
        elif (rlx < mrx and mrx < rrx) and (ruy < mdy and mdy < rdy):
                self.robot_and_monster_collided(); time.sleep(1)
    
    def robot_coin_collision_check(self):
        # see the function above for coordinate (rlx,rrx,ruy,rdy) explanation
        rlx = self.robot_x; rrx = self.robot_x + self.robot.get_width()
        ruy = self.robot_y; rdy = self.robot_y + self.robot.get_height()
        for coin in self.coin_list:
            # coin center has to be in the robot's area
            if rlx < coin.x+20 and coin.x+20 < rrx:
                if ruy < coin.y+20 and coin.y+20 < rdy:
                    self.points += 1
                    coin.x, coin.y = self.coin_new_coordinates()  # creating new x and y
    
    def robot_and_monster_collided(self):
        if self.lives > 0:
            self.deduct_life()
        elif self.lives == 0:
            self.game_over()

    def deduct_life(self):
        collision_text = pygame.font.SysFont("Arial", 32)
        self.window.blit(collision_text.render(f"Contant with the monster", True, (255, 0, 0)), (270, 270))
        pygame.display.flip()
        self.lives -= 1
        self.set_monster_to_origo()  # monster is placed back to (0, 0)
   
    def game_over(self):
        self.window.fill((0,0,0))
        game_over_font = pygame.font.SysFont("Arial", 72)
        self.window.blit(game_over_font.render(f"GAME OVER", True, (255, 0, 0)), (250, 250))
        pygame.display.flip()
        time.sleep(10)  # after game end window is open for 10 and then closes
        # a furhter functionality would be to offer a new game or end the game
        self.end_of_game = True
        
    def main_loop(self):
        while self.end_of_game == False:
            self.check_events()
            self.draw_window()
    
    def check_events(self):
        for event in pygame.event.get():
            # moving the robot manually
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: self.to_left = True
                if event.key == pygame.K_RIGHT: self.to_right = True
                if event.key == pygame.K_UP: self.to_up = True
                if event.key == pygame.K_DOWN: self.to_down = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT: self.to_left = False
                if event.key == pygame.K_RIGHT: self.to_right = False
                if event.key == pygame.K_UP: self.to_up = False
                if event.key == pygame.K_DOWN: self.to_down = False

            if event.type == pygame.QUIT:
                exit()
        
        # moving the robot if any of the keys pressed down, function robot_move() above
        if self.to_left or self.to_right or self.to_up or self.to_down:
            self.robot_move()

        self.monster_movement()  # monster movement is automatic
        self.coin_movement()     # coin movement is automatic

        self.robot_monster_collision_check()  # checking if robot and monster collided
        self.robot_coin_collision_check()     # checking if robot and any of the coins collided

        self.clock.tick(60)
    
    def draw_window(self):
        self.window.fill((150,150,150))
        self.window.blit(self.game_font.render(f"Points: {self.points}", True, (255, 0, 0)), (720, 10))
        self.window.blit(self.game_font.render(f"Lives left: {self.lives}", True, (255, 0, 0)), (720, 35))
        self.window.blit(self.robot, (self.robot_x, self.robot_y))
        self.window.blit(self.monster, (self.monster_x, self.monster_y))
        for coin in self.coin_list:
            self.window.blit(self.coin, (coin.x, coin.y))
        pygame.display.flip()

if __name__ == "__main__":
    RoboCoin()
