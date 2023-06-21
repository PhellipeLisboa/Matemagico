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
high_score = 0
game_over = False
next_wave = False
enemy_timer = 2500
last_enemy = pygame.time.get_ticks()
enemies_alive = 0
player_result = ''
player_result_check = ''

# Carregar recorde
if os.path.exists('recorde.txt'):
    with open('recorde.txt', 'r') as file:
        high_score = int(file.read())

# Definindo cores

black = (0, 0, 0)

# Definindo as fontes

font1 = pygame.font.SysFont('mspgothic', 25)
font2 = pygame.font.SysFont('mspgothic', 70)
# print(pygame.font.get_fonts())

# Carregar imagem da tela inicial

initial_screen = pygame.image.load('imagens/tela inicial/tela inicial.jpg').convert_alpha()

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

# Carregando a musica de fundo
pygame.mixer.music.load('sons/backgroundmusic.mp3')
pygame.mixer.music.play(-1)
fireball_sound = pygame.mixer.Sound('sons/fireball.mp3')
wave_complete_sound = pygame.mixer.Sound('sons/wavecomplete.mp3')
game_over_sound = pygame.mixer.Sound('sons/gameover.mp3')


def create_operation():
    # Criando operações

    # Gerar o primeiro e o segundo número e definir o sinal da operação
    operation_list = ['+', '-', 'x']
    operation = operation_list[random.randint(0, 2)]

    n1 = random.randint(0, target_difficulty // 1)
    if target_difficulty // 1 > 10 and operation == 'x':
        n2 = random.randint(0, 10)
        while n2 > n1:
            n2 = random.randint(0, 10)
    else:
        n2 = random.randint(0, target_difficulty // 1)
        while n2 > n1:
            n2 = random.randint(0, target_difficulty // 1)

    if operation == '+':
        result = n1 + n2
    elif operation == '-':
        result = n1 - n2
    else:
        result = n1 * n2

    return [n1, n2, operation, str(result)]


# Função para escrever textos na tela
def draw_text(text, font, color, x, y):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (x, y))


# Função para mostrar informações
def show_information():
    draw_text('Vida: ' + str(mage.health) + '/' + str(mage.max_health), font1, black, 215, 610)
    draw_text('Pontuação: ' + str(mage.score), font1, black, 90, 340)
    draw_text('Recorde:   ' + str(high_score), font1, black, 90, 370)
    draw_text('RODADA: ' + str(wave), font2, black, 630, 70)
    draw_text(f'{operation_info[0]} {operation_info[2]} {operation_info[1]} = ?', font2, black, 610, 160)
    draw_text(f'RESPOSTA:{player_result}', font2, black, 560, 240)


# Função para desenhar a tela inicial
def draw_initial_screen():
    screen.blit(initial_screen, (0, 0))


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
        global operation_info
        # Soltar bola de fogo
        if player_result_check == operation_info[3] and self.attacking is False:
            self.attacking = True
            fireball = Fireball(fireball_img2, fireball_animation, self.rect.midright[0] - 50,
                                self.rect.midright[1] - 55)
            fireball_group.add(fireball)
            fireball_sound.play()
            operation_info = create_operation()

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

# Criando variaveis da primeira operação
operation_info = create_operation()

# Tela inicial do jogo (instruções)
while True:
    clock.tick(fps)
    pygame.mixer.music.pause()

    # Desenhando a tela inicial
    draw_initial_screen()
    if pygame.mouse.get_pressed()[0]:
        pygame.mixer.music.unpause()
        break

    # Desenhando o cursor

    crosshair.draw()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    pygame.display.update()

# Tela principal do jogo + game over
while True:
    clock.tick(fps)

    if game_over is False:

        screen.fill(black)

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

        # Desenhando as bolas de fogo
        fireball_group.update()

        # Desenhando inimigos
        enemy_group.update(screen, mage, fireball_group)

        # Botando as informações na tela
        show_information()

        # Desenhando o cursor
        crosshair.draw()

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
            wave_complete_sound.play()

            if pygame.time.get_ticks() - wave_reset_time > 1500:
                next_wave = False
                wave += 1
                last_enemy = pygame.time.get_ticks()
                target_difficulty *= difficulty_multiplier
                wave_difficulty = 0
                enemy_group.empty()

        # Verificando se é game over
        if mage.health <= 0:
            # Atualizando o recorde
            if mage.score > high_score:
                high_score = mage.score
                with open('recorde.txt', 'w') as file:
                    file.write(str(high_score))
            pygame.mixer.music.stop()
            game_over_sound.play()
            game_over = True

    else:
        # Textos para tela de game over
        game_over_text = font2.render("GAME OVER", True, (100, 100, 100))
        score_text = font1.render(f"PONTUAÇÃO: {mage.score}", True, (100, 100, 100))
        high_score_text = font1.render(f"RECORDE: {high_score}", True, (100, 100, 100))
        restart_text = font2.render("CLIQUE NA TELA PARA JOGAR NOVAMENTE", True, (81, 81, 81))
        # Desenhando a tela de game over
        screen.fill((0, 0, 0))
        screen.blit(game_over_text, (screen_width / 2 - game_over_text.get_width() / 2, 100))
        screen.blit(score_text, (screen_width / 2 - score_text.get_width() / 2, 300))
        screen.blit(high_score_text, (screen_width / 2 - high_score_text.get_width() / 2, 400))
        screen.blit(restart_text, (screen_width / 2 - restart_text.get_width() / 2, 520))
        crosshair.draw()

        if pygame.mouse.get_pressed()[0]:
            # Reiniciando as variáveis do jogo
            game_over = False
            wave = 1
            wave_difficulty = 0
            target_difficulty = 7
            last_enemy = pygame.time.get_ticks()
            enemy_group.empty()
            fireball_group.empty()
            mage.score = 0
            mage.health = 100
            player_result = ''
            player_result_check = ''
            pygame.mixer.music.play(-1)

    for event in pygame.event.get():
        # Inserindo a resposta pelo teclado
        if event.type == pygame.TEXTINPUT:
            player_result += event.text

        # Configurando o backspace
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                player_result = player_result[:-1]

        # Configurando o envio da resposta
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                player_result_check = player_result
                player_result = ''
                # Impedindo que o mago ataque em looping
                mage.attacking = False

        if event.type == QUIT:
            pygame.quit()
            exit()

    pygame.display.update()
