import pygame


class Inimigo(pygame.sprite.Sprite):
    def __init__(self, health, enemy_animation, x, y, speed, damage):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.health = health
        self.damage = damage
        self.last_attack = pygame.time.get_ticks()
        self.attack_cooldown = 700
        self.enemy_animation = enemy_animation
        self.frame_index = 0
        self.action = 0  # 0 = andar, 1 = atacar, 2 = morrer
        self.update_time = pygame.time.get_ticks()

        # Selecionando a imagem inicial
        self.image = self.enemy_animation[self.action][self.frame_index]
        self.rect = pygame.Rect(0, 0, 110, 150)
        self.rect.center = (x, y)

    def update(self, surface, target, fireball_group):

        if self.alive:

            # Verificando a colisão com as bolas de fogo
            if pygame.sprite.spritecollide(self, fireball_group, True):
                # Diminuindo a vida do inimigo
                self.health -= 1

            # Movendo o inimigo
            if self.action == 0:
                self.rect.x -= self.speed

            # Atacar
            if self.action == 1:
                # Verificando se já passou tempo suficiente desde o último ataque
                if pygame.time.get_ticks() - self.last_attack > self.attack_cooldown:
                    target.health -= self.damage
                    if target.health < 0:
                        target.health = 0
                    self.last_attack = pygame.time.get_ticks()

            # Verificando se o inimigo chegou ao mago
            if self.rect.left < target.rect.right:
                self.update_action(1)

            # Verificando se a vida chegou a zero
            if self.health <= 0:
                target.score += int(self.damage / 5)
                self.update_action(2)  # Morrer
                self.alive = False

        self.update_animation()

        # Desenhando a imagem na tela
        surface.blit(self.image, (self.rect.x - 20, self.rect.y + 5))

    def update_animation(self):
        # Definindo o tempo de recarga da animação
        animation_cooldown = 190

        # Atualizando a imagem de acordo com a ação
        self.image = self.enemy_animation[self.action][self.frame_index]
        # Verificando se já passou tempo suficiente desde a ultima atualização
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # Voltar ao início da animação assim que ela acabar
        if self.frame_index >= len(self.enemy_animation[self.action]):
            if self.action == 2:
                self.frame_index = len(self.enemy_animation[self.action]) - 1
                pass
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Verificar se a nova ação é diferente da atual
        if new_action != self.action:
            self.action = new_action
            # Atualizando as configurações de animação
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

