# Bombardeo del bosque
# Ricardo Nájera / Tomado de 'Mark Cunningham - Game programming with Code Angel'
# 07/07/2020

import sys
import os
import pygame
from pygame.locals import *

# Definiendo los colores
BLANCO = (255, 255, 255)
MORADO = (96, 85, 154)
CLARO_AZUL = (157, 220, 241)
OSCURO_AZUL = (63, 111, 182)
VERDE = (57, 180, 22)

# Definiendo las constántes
ANCHO_PANTALLA = 640
ALTO_PANTALLA = 480
MARGEN_PUNTAJES = 4
ALTO_LINEA = 18
ANCHO_CAJA = 400
ALTO_CAJA = 150

NIVELES_TOTALES = 4
MAX_ARBOLES = 12
ESPACO_ARBOLES = 40
PRIMER_ARBOL = 140
ALTO_TIERRA = 8
ARBOL_FUERA_TIERRA = 20

AVION_INICIO_X = 0
AVION_INICIO_Y = 54

# Setup
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()
pantalla_juego = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption('Bombardeo del bosque')
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont('Helvetica', 16)

# Cargar imagenes
fondo_imagen = pygame.image.load('background.png').convert()
arbol_imagen = pygame.image.load('tree.png').convert_alpha()
arbol_quemado_imagen = pygame.image.load('burning_tree.png').convert_alpha()
avion_imagen = pygame.image.load('plane.png').convert_alpha()
avion_quemado_imagen = pygame.image.load('burning_plane.png').convert_alpha()
bomba_imagen = pygame.image.load('bomb.png').convert_alpha()

# Cargar sonidos
explosion_sonido = pygame.mixer.Sound('explosion.ogg')
arbol_sonido = pygame.mixer.Sound('tree_explosion.ogg')

# Inicializando las variables
nivel = 1
puntaje = 0
puntaje_max = 0
mejora_velocidad = 0

avion_explotado = False
nivel_completado = False
frente_avion = 0
avion_explotado_sonido_ejecutado = False

bomba_soltada = False
bomba = bomba_imagen.get_rect()

avion = avion_imagen.get_rect()
avion.x = AVION_INICIO_X
avion.y = AVION_INICIO_Y

arbol = avion_imagen.get_rect()
arbol.y = ALTO_PANTALLA - arbol.height - ARBOL_FUERA_TIERRA

arbol_quemado = 0
temporizador_arbol = 0

arboles_quemados = []

# Los bosques de cada nivel
bosque_1 = ['T', '-', 'T', '-', '-', '-', 'T', '-', '-', '-', '-', 'T']
bosque_2 = ['-', 'T', '-', '-', 'T', '-', 'T', '-', 'T', 'T', '-', 'T']
bosque_3 = ['T', 'T', '-', '-', 'T', '-', 'T', 'T', 'T', 'T', '-', '-']
bosque_4 = ['T', 'T', '-', '-', 'T', 'T', 'T', '-', 'T', 'T', 'T', '-']
bosque = list(bosque_1)

# Bucle principal
while True:

    for event in pygame.event.get():

        # Barra espacio presionada, suelta la bomba
        tecla_presionada = pygame.key.get_pressed()
        if tecla_presionada[pygame.K_SPACE]:
            if bomba_soltada is False and nivel_completado is False and avion_explotado is False:
                bomba_soltada = True
                bomba.x = avion.x + 15
                bomba.y = avion.y + 10

        # Tecla ENTER al final del juego
        elif tecla_presionada[pygame.K_RETURN]:
            # El avión ha explotado o los niveles se han completado: Volver al inicio
            if avion_explotado is True or (nivel == NIVELES_TOTALES and nivel_completado is True):
                avion_explotado = False
                avion_explotado_sonido_ejecutado = False
                puntaje = 0
                mejora_velocidad = 0
                nivel = 1
                bosque = list(bosque_1)
                avion.x = AVION_INICIO_X
                avion.y = AVION_INICIO_Y
                nivel_completado = False

            # Pasar al siguente nivel
            elif nivel_completado is True:
                nivel += 1
                nivel_completado = False

                if nivel == 2:
                    bosque = list(bosque_2)
                elif nivel == 3:
                    bosque = list(bosque_3)
                    mejora_velocidad = 1
                else:
                    bosque = list(bosque_4)
                    mejora_velocidad = 1

                avion.x = AVION_INICIO_X
                avion.y = AVION_INICIO_Y

        # Salir
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Actualizando la ubicación del avión
    if nivel_completado is False and avion_explotado is False:
        avion.x = avion.x + 5 + mejora_velocidad

    if avion.x >= ANCHO_PANTALLA:
        avion.x = 0
        avion.y += 100

    if bomba_soltada is True:
        bomba.y += 5
        bomba.x += 3

        if bomba.y > ALTO_PANTALLA or bomba.x > ANCHO_PANTALLA:
            bomba_soltada = False

        # Revisar si una bomba golpea un arbol
        for column, bosque_item in enumerate(bosque):
            if bosque_item == 'T':
                arbol.x = PRIMER_ARBOL + column*ESPACO_ARBOLES

                if bomba.colliderect(arbol):
                    bosque[column] = 'B'
                    bomba_soltada = False
                    arboles_quemados.append(column)
                    temporizador_arbol = 10
                    puntaje += 10*nivel
                    arbol_sonido.play()

    if temporizador_arbol > 0:
        temporizador_arbol -= 1
        if temporizador_arbol == 0:
            for column in arboles_quemados:
                bosque[column] = '_'
                del arboles_quemados[:]

    # Avión toca el suelo
    if avion.y >= ALTO_PANTALLA - avion.height - ALTO_TIERRA:
        frente_avion = avion.x + avion.width

        # El borde derecho de la pantalla se alcanza sin colisionar, nivel completado
        if frente_avion >= ANCHO_PANTALLA:
            nivel_completado = True

        # Revisar si el avión colisionó con un árbol
        else:
            for column, bosque_item in enumerate(bosque):
                if bosque_item == 'T' or bosque_item == 'B':
                    arbol_restante = PRIMER_ARBOL + column*ESPACO_ARBOLES
                    if frente_avion >= arbol_restante:
                        avion_explotado = True

    if puntaje > puntaje_max:
        puntaje_max = puntaje

    # Dibujando el fondo
    pantalla_juego.blit(fondo_imagen, [0, 0])  # blit dibuja una imagen en la pantalla de pygame

    # Dibujando el bosque
    for column, bosque_item in enumerate(bosque):
        arbol.x = PRIMER_ARBOL + column*ESPACO_ARBOLES
        if bosque_item == 'T':
            pantalla_juego.blit(arbol_imagen, [arbol.x, arbol.y])
        elif bosque_item == 'B':
            pantalla_juego.blit(arbol_quemado_imagen, [arbol.x, arbol.y])

    # Dibujando el avión
    if avion_explotado is False:
        pantalla_juego.blit(avion_imagen, [avion.x, avion.y])
    else:
        avion.y = ALTO_PANTALLA - avion_quemado_imagen.get_height() - ARBOL_FUERA_TIERRA
        pantalla_juego.blit(avion_quemado_imagen, [avion.x, (avion.y + 15)])

    # Dibujar la bomba
    if bomba_soltada is True:
        pantalla_juego.blit(bomba_imagen, [bomba.x, bomba.y])

    # Mostrar la tabla de puntaje, nivel y puntaje max
    puntaje_fondo_rect = (0, 0, ANCHO_PANTALLA, ALTO_LINEA + 2*MARGEN_PUNTAJES)
    pygame.draw.rect(pantalla_juego, CLARO_AZUL, puntaje_fondo_rect)

    TEXTO_PUNTAJE = 'Puntaje: ' + str(puntaje)
    texto = fuente.render(TEXTO_PUNTAJE, True, MORADO)
    pantalla_juego.blit(texto, [MARGEN_PUNTAJES, MARGEN_PUNTAJES])

    puntMax_texto = 'Puntaje máximo: ' + str(puntaje_max)
    texto = fuente.render(puntMax_texto, True, MORADO)
    rect_texto = texto.get_rect()
    pantalla_juego.blit(texto, [ANCHO_PANTALLA - rect_texto.width - MARGEN_PUNTAJES, MARGEN_PUNTAJES])

    TEXTO_NIVEL = 'Nivel: ' + str(nivel)
    texto = fuente.render(TEXTO_NIVEL, True, MORADO)
    rect_texto = texto.get_rect()
    pantalla_juego.blit(texto, [(ANCHO_PANTALLA - rect_texto.width)/2, MARGEN_PUNTAJES])

    # Mensaje de fin del juego/nivel
    if avion_explotado is True or nivel_completado is True:

        if avion_explotado is True:
            linea_texto_1 = fuente.render('Abríte que ya perdiste gonorrea', True, BLANCO)
            rect_texto_1 = linea_texto_1.get_rect()

            linea_texto_2 = fuente.render('Presiona ENTER pa empezar otra vez.', True, BLANCO)
            rect_texto_2 = linea_texto_2.get_rect()

            if avion_explotado_sonido_ejecutado is False:
                explosion_sonido.play()
                avion_explotado_sonido_ejecutado = True

        elif nivel == NIVELES_TOTALES:
            linea_texto_1 = fuente.render('Cule desocupao, te pasaste esta mondá jajaja')
            rect_texto_1 = linea_texto_1.get_rect()

            linea_texto_2 = fuente.render('Presiona ENTER para empezar otro juego.')
            rect_texto_2 = linea_texto_2.get_rect()

        else:
            linea_texto_1 = fuente.render('NIVEL ' + str(nivel) + ' COMPLETADO.', True, BLANCO)
            rect_texto_1 = linea_texto_1.get_rect()

            linea_texto_2 = fuente.render('Presiona ENTER para pasar al siguente nivel.', True, BLANCO)
            rect_texto_2 = linea_texto_2.get_rect()

        # Mostrar caja de mensaje
        msj_bk_rect = ((ANCHO_PANTALLA - ANCHO_CAJA)/2, (ALTO_PANTALLA - ALTO_CAJA)/2, ANCHO_CAJA, ALTO_CAJA)
        pygame.draw.rect(pantalla_juego, OSCURO_AZUL, msj_bk_rect)

        # Mostrar mensaje de dos lineas
        pantalla_juego.blit(linea_texto_1, [(ANCHO_PANTALLA - rect_texto_1.width)/2,
                                            (ALTO_PANTALLA - rect_texto_1.height)/2 - ALTO_LINEA])
        pantalla_juego.blit(linea_texto_2, [(ANCHO_PANTALLA - rect_texto_2.width)/2,
                                            (ALTO_PANTALLA - rect_texto_2.height)/2 + ALTO_LINEA])

    pygame.display.update()
    reloj.tick(30)
