import random
import sys
import pygame
import pygame.freetype
import math

pygame.init()

pygame.freetype.init()
myfont = pygame.freetype.SysFont(None, 20)

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ping")

clock = pygame.time.Clock()

continuer = True

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
JAUNE = (255, 255, 0)

RAYON_BALLE = 10
XMIN, YMIN = 0, 0
XMAX, YMAX = width, height


class Balle:
    def vitesse_par_angle(self, angle):
        self.vx = self.vitesse * math.cos(math.radians(angle))
        self.vy = -self.vitesse * math.sin(math.radians(angle))

    def __init__(self):
        self.x, self.y = (400, 400)
        self.vitesse = 8
        self.vitesse_par_angle(random.randint(10, 170))
        self.sur_raquette = True
        self.couleur = BLANC

    def afficher(self):
        pygame.draw.rect(screen, self.couleur, (int(self.x-RAYON_BALLE), int(self.y-RAYON_BALLE),
                                         2 * RAYON_BALLE, 2 * RAYON_BALLE), 0)

    def rebond_raquette(self, raquette):
        diff = raquette.x - self.x
        longueur_totale = raquette.longueur/2 + RAYON_BALLE
        angle = 90 + 80 * diff/longueur_totale
        self.vitesse_par_angle(angle)

    def deplacer(self, raquette):
        tombe = False
        if self.sur_raquette:
            self.y = raquette.y - 2 * RAYON_BALLE
            self.x = raquette.x
        else:
            self.x += self.vx
            self.y += self.vy
            if raquette.collision_balle(self) and self.vy > 0:
                self.rebond_raquette(raquette)
            if self.x + RAYON_BALLE > XMAX:
                self.vx = -self.vx
            if self.x - RAYON_BALLE < XMIN:
                self.vx = -self.vx
            if self.y + RAYON_BALLE > YMAX:
                self.sur_raquette = True
                tombe = True
            if self.y - RAYON_BALLE < YMIN:
                self.vy = -self.vy
        return tombe


class Jeu:
    def __init__(self):
        self.jeu = True
        self.balle = Balle()
        self.balle_deux = Balle()
        self.balle_bonus = False
        self.raquette = Raquette()
        coor_briques = []
        for i in range(40, 780, 80):
            for j in range(50, 230, 50):
                coor_briques.append((i, j))
        niveau_deux = [(i, j) for i in range(240, 600, 160) for j in range(95, 185, 75)]
        niveau_trois = [(i, j) for i in range(90, 750, 160) for j in range(100, 230, 75)]
        niveau_quatre = [(i, j) for i in range(40, 780, 80) for j in range(50, 230, 50)]
        self.briques = {1: [Brique(420, 140)], 2: [Brique(x, y) for x, y in niveau_deux],
                        3: [Brique(x, y) for x, y in niveau_trois], 4: [Brique(x, y) for x, y in niveau_quatre]}
        briques_trois = random.sample(self.briques[3], 2)
        for brique in self.briques[3]:
            if brique in briques_trois:
                brique.vie = 2
        brique_quatre = random.sample(self.briques[4], 7)
        for brique in self.briques[4]:
            if brique in brique_quatre:
                if brique == brique_quatre[-1]:
                    brique.vie = 3
                elif brique == brique_quatre[0]:
                    brique.bonus = True
                else:
                    brique.vie = 2
        self.vies = 2
        self.score = 0
        self.score_a_augmente = False
        self.niveau = 1

    def gestion_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.jeu:
                    self.__init__()
                elif event.button == 1:
                    if self.balle.sur_raquette:
                        self.balle.sur_raquette = False
                        self.balle.vitesse_par_angle(random.randint(10, 170))

    def mise_a_jour(self):
        if self.jeu:
            x, y = pygame.mouse.get_pos()
            briques = False
            if self.balle_deux.deplacer(self.raquette):
                self.balle_bonus = False
            if self.balle.deplacer(self.raquette):
                self.vies -= 1
                if self.vies == 0:
                    self.jeu = False
            brique_touche = False
            for brique in self.briques[self.niveau]:
                if brique.en_vie():
                    briques = True
                    if not brique_touche:
                        brique_touche, bonus = brique.collision_balle(self.balle)
                        if not brique_touche and self.balle_bonus:
                            brique_touche, bonus = brique.collision_balle(self.balle_deux)
            if brique_touche:
                self.score += 100
                self.score_a_augmente = True
                if bonus:
                    self.balle_bonus = True
                    self.balle_deux.sur_raquette = False
                    self.balle_deux.couleur = JAUNE
            if not briques:
                self.niveau += 1
                self.balle.sur_raquette = True
                balle_bonus = False
                if self .niveau >= 5:
                    self.jeu = False
            if self.score_a_augmente and self.score % 2000 == 0:
                self.vies += 1
                self.score_a_augmente = False
            self.raquette.deplacer(x)

    def affichage(self):
        screen.fill(NOIR)
        if not self.jeu:
            if self.vies != 0:
                texte, rect = myfont.render("GAGNÉ !", BLANC, size=10*RAYON_BALLE)
                rect.center = (XMAX // 2, YMAX // 2 - 5 * RAYON_BALLE)
                screen.blit(texte, rect)
                texte, rect = myfont.render(f"SCORE : {self.score * self.vies}", BLANC, size=8*RAYON_BALLE)
                rect.center = (XMAX // 2, YMAX // 2 + 5 * RAYON_BALLE)
                screen.blit(texte, rect)
            else:
                texte, rect = myfont.render("GAME OVER", BLANC, size=10*RAYON_BALLE)
                rect.center = (XMAX // 2, YMAX // 2 - 5 * RAYON_BALLE)
                screen.blit(texte, rect)
                texte, rect = myfont.render(f"SCORE : {self.score}", BLANC, size=8*RAYON_BALLE)
                rect.center = (XMAX // 2, YMAX // 2 + 5 * RAYON_BALLE)
                screen.blit(texte, rect)
        else:
            texte, rect = myfont.render(f"Vies : {self.vies}", BLANC, size=RAYON_BALLE * 2)
            rect.midright = (XMAX - 2 * RAYON_BALLE, YMIN + 2 * RAYON_BALLE)
            screen.blit(texte, rect)
            texte, rect = myfont.render(f"NIVEAU {self.niveau}", BLANC, size=RAYON_BALLE*3)
            rect.center = (XMAX // 2, YMIN + 1.5 * RAYON_BALLE)
            screen.blit(texte, rect)
            if self.balle_bonus:
                self.balle_deux.afficher()
            self.balle.afficher()
            self.raquette.afficher()
            for brique in self.briques[self.niveau]:
                if brique.en_vie():
                    brique.afficher()
            texte, rect = myfont.render(f"Score : {self.score}", BLANC, size=RAYON_BALLE * 2)
            rect.midleft = (XMIN + 2 * RAYON_BALLE, YMIN + 2 * RAYON_BALLE)
            screen.blit(texte, rect)


class Raquette:
    def __init__(self):
        self.x = (XMIN + XMAX) / 2
        self.y = YMAX - RAYON_BALLE
        self.longueur = 10 * RAYON_BALLE

    def afficher(self):
        pygame.draw.rect(screen, BLANC, (int(self.x - self.longueur / 2), int(self.y - RAYON_BALLE),
                                         self.longueur, 2 * RAYON_BALLE), 0)

    def deplacer(self, x):
        if x - self.longueur / 2 < XMIN:
            self.x = XMIN + self.longueur / 2
        elif x + self.longueur / 2 > XMAX:
            self.x = XMAX - self.longueur / 2
        else:
            self.x = x

    def collision_balle(self, balle):
        vertical = abs(self.y - balle.y) < 2 * RAYON_BALLE
        horizontal = abs(self.x - balle.x) < self.longueur / 2 + RAYON_BALLE
        return vertical and horizontal


class Brique:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vie = 1
        self.longueur = 5 * RAYON_BALLE
        self.largeur = 3 * RAYON_BALLE
        self.bonus = False

    def en_vie(self):
        return self.vie > 0

    def afficher(self):
        couleurs_vie = {1: BLANC, 2:VERT, 3:ROUGE}
        if self.bonus == True:
            couleur = JAUNE
        else:
            couleur = couleurs_vie[self.vie]
        pygame.draw.rect(screen, couleur, (int(self.x - self.longueur/2), int(self.y - self.largeur/2),
                                         self.longueur, self.largeur), 0)

    def collision_balle(self, balle):
        marge = self.largeur/2 + RAYON_BALLE
        dy = balle.y - self.y
        touche = False
        if balle.x >= self.x:
            dx = balle.x - (self.x + self.longueur/2 - self.largeur/2)
            if abs(dy) <= marge and dx <= marge:
                touche = True
                if dx < abs(dy):
                    balle.vy = -balle.vy
                else:
                    balle.vx = -balle.vx
        else:
            dx = balle.x - (self.x - self.longueur/2 - self.largeur/2)
            if abs(dy) <= marge and -dx <= marge:
                touche = True
                if -dx < abs(dy):
                    balle.vy = -balle.vy
                else:
                    balle.vx = -balle.vx

        if touche:
            self.vie -= 1
        return touche, self.bonus

jeu = Jeu()

while True:
    jeu.gestion_evenements()
    jeu.mise_a_jour()
    jeu.affichage()

    pygame.display.flip()
    clock.tick(60)
