import pygame
from pygame.locals import *
from sys import exit
import random
import os
from inimigo import Inimigo


pygame.init()
clock = pygame.time.Clock()
fps = 60

# Janela do jogo
screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Matemágico')

# Definindo variáveis do jogo
wave = 1
wave_difficulty = 0
target_difficulty = 7
difficulty_multiplier = 1.1
hight_score = 0
game_over = False
next_wave = False
enemy_timer = 2500
last_enemy = pygame.time.get_ticks()
enemies_alive = 0

# Definindo cores

black = (0, 0, 0)

# Definindo as fontes

font1 = pygame.font.SysFont('mspgothic', 25)
font2 = pygame.font.SysFont('mspgothic', 70)
# print(pygame.font.get_fonts())


# Carregar imagem de plano de fundo
background = pygame.image.load('imagens/Plano de fundo/plano de fundo.jpg').convert_alpha()

# Carregar imagem da torre
tower_img = pygame.image.load('imagens/torre/0.png').convert_alpha()
tower = pygame.transform.scale(tower_img, (tower_img.get_width() * 0.55,
                                           tower_img.get_height() * 0.55))

# Carregar imagem da placa de pontuação
score_sign_img = pygame.image.load('imagens/placas/0.png').convert_alpha()
score_sign = pygame.transform.scale(score_sign_img, (score_sign_img.get_width() * 0.55,
                                                     score_sign_img.get_height() * 0.55))

# Carregar imagem da placa onde aparecerão as operações e a rodada atual
operation_sign_img = pygame.image.load('imagens/placas/1.png').convert_alpha()
operation_sign = pygame.transform.scale(operation_sign_img, (operation_sign_img.get_width() * 0.2,
                                                             operation_sign_img.get_height() * 0.15))

# Carregar imagem do personagem
mage_animation = []
for n in range(2):
    mage_img = pygame.image.load(f'imagens/mago/idle/{n}.png').convert_alpha()
    mage_animation.append(mage_img)

# Carregar imagem da bola de fogo
fireball_animation = []
for n in range(3):
    fireball_img = pygame.image.load(f'imagens/bola_de_fogo/{n}.png').convert_alpha()
    fireball_img2 = pygame.transform.scale(fireball_img, (fireball_img.get_width() * 4,
                                                          fireball_img.get_height() * 4))
    fireball_animation.append(fireball_img2)

# Carregar os inimigos
enemy_animation = []
enemy_types = ['orc_vermelho', 'orc_marrom']
enemy_health = [2, 1]
enemy_speed = [1, 2]
enemy_damage = [10, 5]

animation_types = ['andar', 'atacar', 'morrer']
for enemy in enemy_types:
    # Carregar animação
    animation_list = []
    for animation in animation_types:
        # Resetar lista temporária de imagens
        temporary_list = []
        # Definindo número de frames
        if animation == 'andar':
            frames = 6
        else:
            frames = 4
        for i in range(frames):
            img = pygame.image.load(f'imagens/inimigos/{enemy}/{animation}/{i}.png').convert_alpha()
            i_w = img.get_width()
            i_h = img.get_height()
            img = pygame.transform.scale(img, (i_w * 2, i_h * 2))
            temporary_list.append(img)
        animation_list.append(temporary_list)
    enemy_animation.append(animation_list)


# Função para escrever textos na tela
def draw_text(text, font, color, x, y):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (x, y))


# Função para mostrar informações
def show_information():
    draw_text('Vida: ' + str(mage.health) + '/' + str(mage.max_health), font1, black, 215, 610)
    draw_text('Pontuação: ' + str(mage.score), font1, black, 90, 340)
    draw_text('Recorde:   ' + str(hight_score), font1, black, 90, 370)
    draw_text('RODADA: ' + str(wave), font2, black, 630, 70)


# Função para desenhar o plano de fundo
def draw_background():
    screen.blit(background, (0, 0))


# Função para desenhar a torre
def draw_tower():
    screen.blit(tower, (-80, 5))


# Função para desenhar a placa de pontuação
def draw_score_sign():
    screen.blit(score_sign, (70, 310))


# Função para desenhar a placa de operações
def draw_operation_sign():
    screen.blit(operation_sign, (380, -75))


class Mage(pygame.sprite.Sprite):
    def __init__(self, mage_animation, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.health = 100
        self.max_health = self.health
        self.attacking = False
        self.score = 0
        self.mage_animation = mage_animation
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # Selecionando a imagem inicial
        self.image = self.mage_animation[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def atacar(self):
        # Soltar bola de fogo
        if pygame.mouse.get_pressed()[0] and self.attacking is False:
            self.attacking = True
            fireball = Fireball(fireball_img2, fireball_animation, self.rect.midright[0] - 50,
                                self.rect.midright[1] - 55)
            fireball_group.add(fireball)
        if pygame.mouse.get_pressed()[0] is False:
            self.attacking = False

    def update(self):

        self.update_animation()

        # Desenhando a imagem na tela
        screen.blit(self.image, self.rect)

    def update_animation(self):
        # Definindo o tempo de recarga da animação
        animation_cooldown = 300

        # Atualizando a imagem
        self.image = self.mage_animation[self.frame_index]

        # Verificando se já passou tempo suficiente desde a última atualização
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Voltar ao início da animação assim que ela acabar
        if self.frame_index >= len(self.mage_animation):
            self.frame_index = 0


class Fireball(pygame.sprite.Sprite):
    def __init__(self, image, animation, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Selecionando a imagem inicial
        self.animation = fireball_animation
        self.frame_index = 0
        self.image = self.animation[self.frame_index]
        self.rect = pygame.Rect(0, 0, 73, 60)
        self.rect.x = x
        self.rect.y = y
        self.speed = 6
        self.update_time = pygame.time.get_ticks()

    def update(self):

        self.update_animation()

        # Desenhando a imagem na tela
        screen.blit(self.image, (self.rect.x - 20, self.rect.y - 30))

        # Verificando se a bola de fogo saiu da tela
        if self.rect.left > screen_width:
            self.kill()

        self.rect.x += self.speed

    def update_animation(self):
        # Definindo o tempo de recarga da animação
        animation_cooldown = 120

        # Atualizando a imagem
        self.image = self.animation[self.frame_index]

        # Verificando se já passou tempo suficiente desde a última atualização
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Voltar ao início da animação assim que ela acabar
        if self.frame_index >= len(self.animation):
            self.frame_index = 0


class Crosshair:
    def __init__(self, scale):
        image = pygame.image.load('imagens/cursor/0.png').convert_alpha()
        width = image.get_width()
        height = image.get_height()

        self.image = pygame.transform.scale(image, (int(width * scale),
                                                    int(height * scale)))
        self.rect = self.image.get_rect()

        # Escondendo o cursor padrão
        pygame.mouse.set_visible(False)

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        self.rect.center = (mx + 14, my + 19)
        screen.blit(self.image, self.rect)


# Criando o mago
mage = Mage(mage_animation, 290, 525)

# Criando o cursor
crosshair = Crosshair(0.15)

# Criando o grupos
fireball_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

while True:
    clock.tick(fps)

    if game_over is False:
        # Desenhando o plano de fundo
        draw_background()

        # Desenhando a torre
        draw_tower()

        # Desenhando a placa de pontuação
        draw_score_sign()

        # Desenhando a placa de operação
        draw_operation_sign()

        # Desenhando o mago
        mage.update()
        mage.atacar()

        # Desenhando o cursor

        crosshair.draw()

        # Desenhando as bolas de fogo
        fireball_group.update()

        # Desenhando inimigos
        enemy_group.update(screen, mage, fireball_group)

        # Botando as informações na tela
        show_information()

        # Criar inimigos
        # Verificar se o número máximo de inimigos foi atingido
        if wave_difficulty < target_difficulty:
            if pygame.time.get_ticks() - last_enemy > enemy_timer:
                # Criando inimigos
                e = random.randint(0, len(enemy_types) - 1)
                enemy = Inimigo(enemy_health[e], enemy_animation[e],
                                screen_width + 50, 525, enemy_speed[e], enemy_damage[e])
                enemy_group.add(enemy)
                # Resetando o timer
                last_enemy = pygame.time.get_ticks()
                # Aumentando a dificuldade usando a vida dos inimigos
                wave_difficulty += enemy_health[e]

        # Verificar se todos os inimigos foram gerados
        if wave_difficulty >= target_difficulty:
            # Verificar quantos ainda estão vivos
            enemies_alive = 0
            for e in enemy_group:
                if e.alive:
                    enemies_alive += 1
            # Completar a wave se não tiverem mais inimigos vivos
            if enemies_alive == 0 and next_wave is False:
                next_wave = True
                wave_reset_time = pygame.time.get_ticks()

        # Passar para a próxima wave
        if next_wave:
            draw_text('RODADA COMPLETA!', font2, black, 510, 400)

            if pygame.time.get_ticks() - wave_reset_time > 1500:
                next_wave = False
                wave += 1
                last_enemy = pygame.time.get_ticks()
                target_difficulty *= difficulty_multiplier
                wave_difficulty = 0
                enemy_group.empty()

        # Verificando se é game over
        if mage.health <= 0:
            game_over = True

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    pygame.display.update()
