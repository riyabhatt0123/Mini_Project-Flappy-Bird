import pygame as pg # pygame is used for creating games
import sys, time # sys is used to handle system-level operations like exiting the game.
from bird import Bird # time is used for managing the game loop timing.
from pipe import Pipe # Bird and Pipe are custom modules representing the bird and pipes.

# Initializing Pygame and Pygame Mixer:
pg.init() #pg.init() initializes all Pygame modules.
pg.mixer.init() # pg.mixer.init() initializes the Pygame mixer for handling sound.
 
 # Setting Up Basic Game Parameters:
class Game:
    def __init__(self):
        self.scale_factor = 1.5 # scale_factor adjusts the size of game elements.
        self.width = 600   # width and height define the initial window size.
        self.height = 768
        self.win = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
        # self.win creates a resizable Pygame window.

        self.clock = pg.time.Clock() # self.clock manages the frame rate.
        self.move_speed = 250 # move_speed controls how fast elements move on the screen.
        self.start_monitoring = False # start_monitoring tracks whether the bird is in scoring range.
        self.score = 0 # score keeps the player's score.
        '''font, score_text, score_text_rect handle the score display.'''
        self.font = pg.font.Font("assets/font.ttf", 24) 
        self.score_text = self.font.render("Score: 0", True, (0, 0, 0))
        self.score_text_rect = self.score_text.get_rect(center=(100, 30))

        '''restart_text, restart_text_rect handle the restart button display.'''
        self.restart_text = self.font.render("Restart", True, (0, 0, 0))
        self.restart_text_rect = self.restart_text.get_rect(center=(300, 700))

        #Initializes the bird object.
        self.bird = Bird(self.scale_factor)

        self.is_enter_pressed = False
        self.is_game_started = True
        self.is_game_paused = False
        self.hit_sound_played = False
        self.pipes = [] # pipes list holds pipe objects.
        self.pipe_generate_counter = 71 # pipe_generate_counter helps with timing pipe generation.

        '''setUpBgAndGround loads and positions background and ground images.
        loadSounds loads game sounds.
        gameLoop starts the main game loop.'''
        self.setUpBgAndGround()
        self.loadSounds()
        
        self.gameLoop()
    
    #Continuously runs until the game exits.
    def gameLoop(self):
        last_time = time.time()
        while True:
            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time

        # Handles user inputs and window events.
        # Toggles pause with the K key.
        #Starts the game with the Enter key. 
        #Makes the bird flap with the Space key, playing the flap sound.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_k:
                        self.togglePause()
                    if event.key == pg.K_RETURN and self.is_game_started and not self.is_game_paused:
                        self.is_enter_pressed = True
                        self.bird.update_on = True
                    if event.key == pg.K_SPACE and self.is_enter_pressed and not self.is_game_paused:
                        self.bird.flap(dt)
                        self.flap_sound.play()
                # Restarts the game if the restart button is clicked.        
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.restart_text_rect.collidepoint(pg.mouse.get_pos()):
                        self.restartGame()
                # Adjusts the game elements when the window is resized.
                if event.type == pg.VIDEORESIZE:
                    self.resizeWindow(event.w, event.h)

            # Updates game elements, checks score, and detects collisions if the game is not paused.
            if not self.is_game_paused:
                self.updateEverything(dt)
                self.CheckScore()
                self.checkCollisions()
            
            # Draws all game elements and updates the display.
            #Maintains a frame rate of 60 FPS(Frame Per Second).
            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

   # Toggles the game's paused state.     
    def togglePause(self):
        self.is_game_paused = not self.is_game_paused

    #Resizes the game window and adjusts game elements accordingly.
    def resizeWindow(self, width, height):
        self.width, self.height = width, height
        self.win = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
        self.scale_factor = min(self.width / 600, self.height / 768)
        self.setUpBgAndGround()
        self.bird.scale(self.scale_factor)
        self.score_text_rect.center = (100 * self.scale_factor, 30 * self.scale_factor)
        self.restart_text_rect.center = (self.width / 2, self.height - 100 * self.scale_factor)

    # Resets the game to its initial state.
    def restartGame(self):
        self.score = 0
        self.score_text = self.font.render("Score: 0", True, (0, 0, 0))
        self.is_enter_pressed = False
        self.is_game_started = True
        self.hit_sound_played = False
        self.pipes.clear()
        self.pipe_generate_counter = 71
        self.bird.update_on = False
        self.bird.resetPosition()

    # Increases the score when the bird successfully passes through pipes and plays the score sound.
    def CheckScore(self):
        if len(self.pipes) > 0:
            if self.bird.rect.left > self.pipes[0].rect_down.left and self.bird.rect.right < self.pipes[0].rect_down.right and not self.start_monitoring:
                self.start_monitoring = True
            if self.bird.rect.left > self.pipes[0].rect_down.right and self.start_monitoring:
                self.start_monitoring = False
                self.score += 1
                self.score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
                self.score_sound.play()

    # Checks if the bird collides with the ground or pipes and plays the hit sound only once per collision.
    def checkCollisions(self):
        if len(self.pipes):
            if self.bird.rect.bottom > self.height - 200 * self.scale_factor:
                self.bird.update_on = False
                self.is_enter_pressed = False
                self.is_game_started = False
                if not self.hit_sound_played:
                    self.hit_sound.play()
                    self.hit_sound_played = True
            if (self.bird.rect.colliderect(self.pipes[0].rect_down) or
            self.bird.rect.colliderect(self.pipes[0].rect_up)):
                self.is_enter_pressed = False
                self.is_game_started = False
                if not self.hit_sound_played:
                    self.hit_sound.play()
                    self.hit_sound_played = True

    #Updates the ground position, generates pipes, updates pipes, and updates the bird.
    def updateEverything(self, dt):
        if self.is_enter_pressed:
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed))
                self.pipe_generate_counter = 0
                
            self.pipe_generate_counter += 1

            for pipe in self.pipes:
                pipe.update(dt)

            if len(self.pipes) != 0:
                if self.pipes[0].rect_up.right < 0:
                    self.pipes.pop(0)
                  
        self.bird.update(dt)

    # Draws the background, pipes, ground, bird, score, and restart text.
    def drawEverything(self):
        self.win.blit(self.bg_img, (0, 0))
        for pipe in self.pipes:
            pipe.drawPipe(self.win)
        self.win.blit(self.ground1_img, self.ground1_rect)
        self.win.blit(self.ground2_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)
        self.win.blit(self.score_text, self.score_text_rect)
        
        if not self.is_game_started:
            self.win.blit(self.restart_text, self.restart_text_rect)

    #Loads and scales the background and ground images, sets their initial positions.
    def setUpBgAndGround(self):
        self.bg_img = pg.transform.scale(pg.image.load("assets/bg.png").convert(), (self.width, self.height))
        self.ground1_img = pg.transform.scale(pg.image.load("assets/ground.png").convert(), (self.width, int(200 * self.scale_factor)))
        self.ground2_img = pg.transform.scale(pg.image.load("assets/ground.png").convert(), (self.width, int(200 * self.scale_factor)))

        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = self.height - 200 * self.scale_factor
        self.ground2_rect.y = self.height - 200 * self.scale_factor

    # Loads the sound files for flap, score, and hit actions.
    def loadSounds(self):
        self.flap_sound = pg.mixer.Sound("assets/sfx/flap.wav")
        self.score_sound = pg.mixer.Sound("assets/sfx/score.wav")
        self.hit_sound = pg.mixer.Sound("assets/sfx/dead.wav")

#Instantiates the Game class, starting the game.
game = Game()
