import pygame
import random
import sys

pygame.init()

# Размеры окна и игровой зоны
WIDTH, HEIGHT = 800, 600
GAME_HEIGHT = 500          # высота игрового поля (без панели управления)
CONTROLS_HEIGHT = HEIGHT - GAME_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Маша сжигает сольфеджио")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PINK = (255, 182, 193)
SKIN = (255, 228, 196)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
BG = (135, 206, 235)

# ---------- Класс кнопки для сенсорного управления ----------
class Button:
    def __init__(self, x, y, width, height, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.pressed = False   # зажата ли сейчас (для движения)

    def draw(self, surface):
        # Рисуем кнопку с полупрозрачностью
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill((*self.color, 150) if not self.pressed else (*self.color, 220))
        surface.blit(s, (self.rect.x, self.rect.y))
        # Текст
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) and self.pressed:
                self.pressed = False
                # Дополнительно можно вернуть False, но не нужно
        elif event.type == pygame.FINGERDOWN:   # мобильные касания
            # Конвертируем координаты касания в оконные
            fx = int(event.x * WIDTH)
            fy = int(event.y * HEIGHT)
            if self.rect.collidepoint(fx, fy):
                self.pressed = True
                return True
        elif event.type == pygame.FINGERUP:
            fx = int(event.x * WIDTH)
            fy = int(event.y * HEIGHT)
            if self.rect.collidepoint(fx, fy):
                self.pressed = False
        return False

# ---------- Класс игрока (Маша) ----------
class Player:
    def __init__(self):
        self.width = 60
        self.height = 80
        self.x = WIDTH // 2 - self.width // 2
        self.y = GAME_HEIGHT - self.height - 10   # стоит на "земле" игрового поля
        self.speed = 7
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0

    def move(self, dx):
        self.x += dx
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

    def draw(self, surface):
        # Тело и платье
        pygame.draw.rect(surface, PINK, (self.x + 15, self.y + 30, 30, 50))
        pygame.draw.line(surface, SKIN, (self.x + 20, self.y + 80), (self.x + 15, self.y + 95), 4)
        pygame.draw.line(surface, SKIN, (self.x + 40, self.y + 80), (self.x + 45, self.y + 95), 4)
        pygame.draw.line(surface, SKIN, (self.x + 10, self.y + 40), (self.x - 5, self.y + 55), 4)
        pygame.draw.line(surface, SKIN, (self.x + 50, self.y + 40), (self.x + 65, self.y + 55), 4)
        # Голова и волосы
        pygame.draw.circle(surface, SKIN, (self.x + 30, self.y + 15), 20)
        pygame.draw.ellipse(surface, BROWN, (self.x + 5, self.y - 5, 50, 20))
        # Лицо
        pygame.draw.circle(surface, BLACK, (self.x + 22, self.y + 12), 3)
        pygame.draw.circle(surface, BLACK, (self.x + 38, self.y + 12), 3)
        if self.invincible:
            pygame.draw.arc(surface, BLACK, (self.x + 20, self.y + 18, 20, 10), 0, 3.14, 2)
        else:
            pygame.draw.arc(surface, BLACK, (self.x + 20, self.y + 22, 20, 8), 3.14, 6.28, 2)

    def hit(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = 60
            if self.lives <= 0:
                return False
        return True

    def update(self):
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

# ---------- Лист сольфеджио ----------
class Sheet:
    def __init__(self, speed):
        self.width = 50
        self.height = 70
        self.x = random.randint(20, WIDTH - 20 - self.width)
        self.y = -self.height
        self.speed = speed
        notes = ["♪", "♫", "♬", "𝄞"]
        self.note = random.choice(notes)
        self.color = (255, 255, 220)

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 2)
        for i in range(5):
            y_line = self.y + 10 + i * 8
            pygame.draw.line(surface, BLACK, (self.x + 5, y_line), (self.x + self.width - 5, y_line), 1)
        note_font = pygame.font.Font(None, 30)
        note_surf = note_font.render(self.note, True, BLACK)
        surface.blit(note_surf, (self.x + 15, self.y + 45))

    def off_screen(self):
        return self.y > GAME_HEIGHT

    def collides_with(self, player):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        sheet_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(sheet_rect)

# ---------- Огненный шар ----------
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = -10

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, ORANGE, (self.x, self.y), self.radius + 2)
        pygame.draw.circle(surface, YELLOW, (self.x, self.y), self.radius - 2)

    def off_screen(self):
        return self.y < -20

    def collides_with(self, sheet):
        bullet_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        sheet_rect = pygame.Rect(sheet.x, sheet.y, sheet.width, sheet.height)
        return bullet_rect.colliderect(sheet_rect)

# ---------- Экраны завершения ----------
def game_over_screen(score):
    screen.fill(BG)
    title = font.render("Игра окончена!", True, RED)
    msg1 = font.render(f"Сожжено листов: {score}", True, BLACK)
    msg2 = font.render("Нажми R для рестарта или Q для выхода", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))
    screen.blit(msg1, (WIDTH//2 - msg1.get_width()//2, HEIGHT//2))
    screen.blit(msg2, (WIDTH//2 - msg2.get_width()//2, HEIGHT//2 + 40))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()

def victory_screen(score):
    screen.fill(BG)
    title = font.render("Поздравляем!", True, GREEN)
    msg1 = font.render(f"Маша сожгла всё сольфеджио! Счёт: {score}", True, BLACK)
    msg2 = font.render("Нажми R для новой игры или Q для выхода", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))
    screen.blit(msg1, (WIDTH//2 - msg1.get_width()//2, HEIGHT//2))
    screen.blit(msg2, (WIDTH//2 - msg2.get_width()//2, HEIGHT//2 + 40))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()

# ---------- Основная игра ----------
def main():
    run = True
    while run:
        player = Player()
        bullets = []
        sheets = []
        score = 0
        base_speed = 2
        level = 1
        level_threshold = 10

        # Создаём кнопки управления (координаты в нижней панели)
        left_btn = Button(30, GAME_HEIGHT + 20, 100, 80, "←", (200, 200, 200))
        right_btn = Button(WIDTH - 130, GAME_HEIGHT + 20, 100, 80, "→", (200, 200, 200))
        fire_btn = Button(WIDTH//2 - 55, GAME_HEIGHT + 10, 110, 90, "ОГОНЬ", (255, 100, 100), WHITE)

        playing = True
        while playing:
            clock.tick(60)

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                # Передаём события кнопкам
                left_btn.handle_event(event)
                right_btn.handle_event(event)
                # Кнопка огня – выстрел при нажатии (не зажатии)
                if fire_btn.handle_event(event):
                    # handle_event возвращает True при нажатии
                    bullet = Bullet(player.x + player.width // 2, player.y - 10)
                    bullets.append(bullet)

                # Клавиатура тоже работает
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullet = Bullet(player.x + player.width // 2, player.y - 10)
                        bullets.append(bullet)

            # Движение с кнопок или клавиш
            keys = pygame.key.get_pressed()
            move_left = keys[pygame.K_LEFT] or left_btn.pressed
            move_right = keys[pygame.K_RIGHT] or right_btn.pressed
            if move_left:
                player.move(-player.speed)
            if move_right:
                player.move(player.speed)

            player.update()

            # Генерация листов
            if random.randint(1, 40) == 1:
                speed_multiplier = 1 + (level - 1) * 0.3
                sheets.append(Sheet(base_speed * speed_multiplier))

            # Обновление листов и столкновения с игроком
            for sheet in sheets[:]:
                sheet.move()
                if sheet.off_screen():
                    sheets.remove(sheet)
                elif sheet.collides_with(player):
                    if not player.hit():
                        game_over_screen(score)
                        playing = False
                        break
                    sheets.remove(sheet)

            # Обновление пуль и попадания
            for bullet in bullets[:]:
                bullet.move()
                if bullet.off_screen():
                    bullets.remove(bullet)
                    continue
                hit = False
                for sheet in sheets[:]:
                    if bullet.collides_with(sheet):
                        sheets.remove(sheet)
                        bullets.remove(bullet)
                        score += 1
                        if score >= level * level_threshold:
                            level += 1
                        hit = True
                        break
                if hit:
                    continue

            # Отрисовка
            screen.fill(BG)
            # Игровое поле (зелёная "земля" по границе GAME_HEIGHT)
            pygame.draw.rect(screen, GREEN, (0, GAME_HEIGHT, WIDTH, CONTROLS_HEIGHT))
            player.draw(screen)
            for sheet in sheets:
                sheet.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)

            # Панель управления (кнопки)
            left_btn.draw(screen)
            right_btn.draw(screen)
            fire_btn.draw(screen)

            # Текстовый интерфейс
            lives_text = font.render(f"Жизни: {player.lives}", True, BLACK)
            score_text = font.render(f"Счёт: {score}", True, BLACK)
            level_text = font.render(f"Уровень: {level}", True, BLACK)
            screen.blit(lives_text, (10, 10))
            screen.blit(score_text, (10, 50))
            screen.blit(level_text, (10, 90))

            pygame.display.flip()

            # Победа при уровне > 5
            if level > 5:
                victory_screen(score)
                playing = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()