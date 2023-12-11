import pygame
import random
import neat
import os
import pickle
from pygame.locals import *

#VARIABLES
play_sounds = False
use_pickle = False
checkpoint_name = "" # if you dont want to use a checkpoint leave this empty! 

SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT= 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'

pygame.mixer.init()



if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt") 
    
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    if use_pickle:
        population_size = 1
    else:
        population_size = config.pop_size
    
    
class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images =  [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2
        self.is_alive = True

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        #UPDATE HEIGHT
        self.rect[1] += self.speed

    def bump(self):
        if play_sounds:
            pygame.mixer.music.load(wing)
            pygame.mixer.music.play()
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]




class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self. image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))
        self.ysize = ysize

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize


        self.mask = pygame.mask.from_surface(self.image)


    def update(self):
        self.rect[0] -= GAME_SPEED

        

class Ground(pygame.sprite.Sprite):
    
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

def restart():
    global birds, bird_group, ground_group, ground, pipe_group, pipes
    
    bird_group = pygame.sprite.Group()
    birds = []
    for i in range(population_size):
        i = Bird()
        birds.append(i)
        bird_group.add(i)

    ground_group = pygame.sprite.Group()

    for i in range (2):
        ground = Ground(GROUND_WIDHT * i)
        ground_group.add(ground)

    pipe_group = pygame.sprite.Group()
    for i in range (2):
        pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])
    
    for bird in birds:
        bird.bump()
    
    pygame.display.update()
    

bird_group = pygame.sprite.Group()
birds = []
for i in range(population_size):
    i = Bird()
    birds.append(i)
    bird_group.add(i)

ground_group = pygame.sprite.Group()

for i in range (2):
    ground = Ground(GROUND_WIDHT * i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range (2):
    pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])
    
    
clock = pygame.time.Clock()


for bird in birds:
    bird.bump()

begin = True

while begin:

    clock.tick(15)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                for bird in birds: 
                    bird.bump()
                begin = False

    screen.blit(BACKGROUND, (0, 0))
    screen.blit(BEGIN_IMAGE, (120, 150))

    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])

        new_ground = Ground(GROUND_WIDHT - 20)
        ground_group.add(new_ground)
    for bird in birds:
        bird.begin()
    ground_group.update()

    bird_group.draw(screen)
    ground_group.draw(screen)

    pygame.display.update()

def find_closest_pipe_differences(bird):
    global pipe_group
    
    closest_pipe = sorted((i for i in list(x for x in pipe_group) if i.rect.x > bird.rect.x-100), key=lambda x: x.rect.x)[0]
    return [closest_pipe.rect.x - bird.rect.x, bird.rect.y - closest_pipe.rect.y-150,bird.rect.y - closest_pipe.rect.y]
    
    
class Game:
    
    def __init__(self, genomes, config):
        self.genomes = genomes
        self.config = config
    def playGame(self):
        nets = []
        if use_pickle:
            for i in self.genomes:
                nets.append(neat.nn.FeedForwardNetwork.create(i, self.config))
        else:
            for i, (genomeid, genome) in enumerate(self.genomes):
                nets.append(neat.nn.FeedForwardNetwork.create(genome, self.config))
        
        while True:

            clock.tick(15)
            
            
            if not use_pickle:
                try:
                    for i, (genomeid, genome) in enumerate(self.genomes):
                        if birds[i].is_alive:
                            genome.fitness += 0.1
                except(IndexError):
                    pass
            
            for i, net in enumerate(nets):      
                output = net.activate(find_closest_pipe_differences(birds[i]))

                
                decisiton = output.index(max(output))
            
                if decisiton == 1 and birds[i].is_alive:
                    birds[i].bump()
                    pass

            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()

            screen.blit(BACKGROUND, (0, 0))

            if is_off_screen(ground_group.sprites()[0]):
                ground_group.remove(ground_group.sprites()[0])

                new_ground = Ground(GROUND_WIDHT - 20)
                ground_group.add(new_ground)

            if is_off_screen(pipe_group.sprites()[0]):
                pipe_group.remove(pipe_group.sprites()[0])
                pipe_group.remove(pipe_group.sprites()[0])

                pipes = get_random_pipes(SCREEN_WIDHT * 2)

                pipe_group.add(pipes[0])
                pipe_group.add(pipes[1])

            bird_group.update()
            ground_group.update()
            pipe_group.update()

            bird_group.draw(screen)
            pipe_group.draw(screen)
            ground_group.draw(screen)

            pygame.display.update()
            for i, bird in enumerate(birds):
                test_group = pygame.sprite.Group()
                test_group.add(bird)
                if (bird.is_alive and pygame.sprite.groupcollide(test_group, ground_group, False, False, pygame.sprite.collide_mask) or
                        pygame.sprite.groupcollide(test_group, pipe_group, False, False, pygame.sprite.collide_mask) or bird.rect.y < 0):
                    if ((bird.is_alive and pygame.sprite.groupcollide(test_group, ground_group, False, False, pygame.sprite.collide_mask) or bird.rect.y < 0)):
                        pass
                    if play_sounds:
                        pygame.mixer.music.load(hit)
                        pygame.mixer.music.play()
                    bird.is_alive = False
                    bird.rect.y -= 1000
                test_group.remove(bird)
            if all(not x.is_alive for x in birds):
                restart()
                break

def eval_genomes(genomes, config):
    for (genomeid, genome) in genomes:
        genome.fitness = 0
    game = Game(genomes, config)
    game.playGame()
        

def run_neat(config, checkpoint=""):
    if checkpoint == "":
        p = neat.Population(config)
    else:
        p = neat.Checkpointer.restore_checkpoint(checkpoint)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))
    
    best = p.run(eval_genomes, 200)
    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)

def use_ai(config):
    with open("best.pickle", "rb") as f:
        best = [pickle.load(f)]
    game = Game(best, config)
    game.playGame()

if __name__ == "__main__":
    if use_pickle:
        use_ai(config)
    else:
        run_neat(config, checkpoint=checkpoint_name)