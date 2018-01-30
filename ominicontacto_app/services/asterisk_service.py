# -*- coding: utf-8 -*-

""" Servicio de interaccion con asterisk"""

from __future__ import unicode_literals

import logging

import MySQLdb

from django.conf import settings
from ominicontacto_app.asterisk_config import (
    SipConfigCreator, SipConfigFile, AsteriskConfigReloader)
from ominicontacto_app.errors import OmlError

logger = logging.getLogger(__name__)


class AsteriskService():
    """
    Este servicio realiza la interaccion con la base de mysql de asterisk
    """

    def _conectar_base_datos(self):
        """
        _conectar_base_datos() returna el connection y el cursor de la base mysql
        """
        connection = MySQLdb.connect(
            db=settings.DATABASE_MYSQL_ASTERISK['BASE'],
            user=settings.DATABASE_MYSQL_ASTERISK['USER'],
            passwd=settings.DATABASE_MYSQL_ASTERISK['PASSWORD'],
            host=settings.DATABASE_MYSQL_ASTERISK['HOST']
        )
        cursor = connection.cursor()
        return connection, cursor

    def insertar_cola_asterisk(self, queue):
        """
        insert cola en asterisk
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """INSERT INTO miscdests (description, destdial) values
                  (%(description)s, %(destdial)s)"""
            params = {
                'description': queue.name,
                'destdial': queue.get_string_queue_asterisk(),
            }
            cursor.execute(sql, params)
            connection.commit()
            connection.close()
        except MySQLdb.DatabaseError, e:
            print "error base de datos"
            connection.close()

    def delete_cola_asterisk(self, queue):
        """
        delete cola en asterisk
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """DELETE FROM miscdests WHERE description=%(description)s"""
            params = {
                'description': queue.name
            }
            cursor.execute(sql, params)
            connection.commit()
            connection.close()
        except MySQLdb.DatabaseError, e:
            print "error base de datos"
            connection.close()


class RestablecerConfigSipError(OmlError):
    """Indica que se produjo un error al crear el config sip."""
    pass


class ActivacionAgenteService(object):
    """Este servicio regenera y recarga los archivos de configuracion para los agentes"""

    def __init__(self):
        self.sip_config_creator = SipConfigCreator()
        self.config_file = SipConfigFile()
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_configuracion_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.sip_config_creator.create_config_sip()
        except:
            logger.exception("ActivacionAgenteService: error al "
                             "intentar create_config_sip()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del config sip de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerConfigSipError(mensaje_error))
        else:
            self.config_file.copy_asterisk()
            self.reload_asterisk_config.reload_asterisk()

    def activar(self):
        self._generar_y_recargar_configuracion_asterisk()
