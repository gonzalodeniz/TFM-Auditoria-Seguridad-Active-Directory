# -*- coding: utf-8 -*-

'''
logeasy.py
Autor: Gonzalo Déniz
Fecha: 21/02/2017
Version: 1.0
Descripción:
    Facilita el uso de los logs.

    Ej. de uso:
    clog_ = logeasy.console_log(name='log_monadlib',
                                level=logging.DEBUG,
                                format=logeasy.F_DEBUG)

    flog = logeasy.file_log(filename='log_monadlib',
                            name='log_monsadlib',
                            filemode='w',
                            level=logging.DEBUG,
                            format=logeasy.F_DEBUG)
'''
import logging

# Constantes
F_INFO = '%(asctime)s [%(levelname)s] %(message)s'
F_DEBUG = '%(asctime)s [%(levelname)s] %(module)s.%(filename)s %(funcName)s:: %(message)s'


def console_log(name=None, level = logging.NOTSET, format=None):
    '''
    Devuelve un objeto log que se visualizar por consola
    Param:
        name:   (string) Nombre del log. Si se omite el log es el raiz de los logs
        level:  (constante de LEVEL). Establece la sensibilidad del log. Por defecto no se muestra nada.
        format: (string) Puede utilizarse F_INFO, F_DEBUG o poner un format personalizado
    return:
        Devuelve un objeto logger
    '''
    log = logging.getLogger(name)
    log.setLevel(level)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(format))
    log.addHandler(sh)
    return log

def file_log(filename, name=None, filemode='a', level = logging.NOTSET, format=None):
    '''
    Escribe en un fichero los logs
    Param:
        filename: (string) Nombre del fichero
        name:   (string) Nombre del log. Si se omite el log es el raiz de los logs
        filemode: (string) Modo de apertura del fichero log: 'a' se concatena. 'w' se sobreescribe.
        level:  (constante de LEVEL). Establece la sensibilidad del log. Por defecto no se muestra nada.
        format: (string) Puede utilizarse F_INFO, F_DEBUG o poner un format personalizado
    return:
        Devuelve un objeto logger
    '''
    log = logging.getLogger(name)
    log.setLevel(level)
    fh = logging.FileHandler(filename, filemode)
    fh.setFormatter(logging.Formatter(format))
    log.addHandler(fh)
    return log
