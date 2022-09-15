# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""
Servicio para generar reporte csv de las reportes en
resultados de base de una campaña determinada
"""

from __future__ import unicode_literals

import csv
import logging
import os
import redis

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.translation import gettext as _
from ominicontacto_app.utiles import crear_archivo_en_media_root

logger = logging.getLogger(__name__)


class ReporteCSV:
    redis_connection = redis.Redis(
        host=settings.REDIS_HOSTNAME,
        port=settings.CONSTANCE_REDIS_CONNECTION['port'],
        decode_responses=True
    )


class CrearArchivoDeReporteCsv(object):

    def __init__(self, campana, nombre_reporte, datos_reporte):
        self._campana = campana
        self.datos_reporte = datos_reporte
        self.nombre_del_directorio = 'reporte_resultados_de_base_campana'
        self.prefijo_nombre_de_archivo = "{0}-{1}".format(
            self._campana.id,
            nombre_reporte
        )
        self.sufijo_nombre_de_archivo = ".csv"
        self.nombre_de_archivo = "{0}{1}".format(
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo
        )
        self.url_descarga = os.path.join(
            settings.MEDIA_URL,
            self.nombre_del_directorio,
            self.nombre_de_archivo
        )
        self.ruta = os.path.join(
            settings.MEDIA_ROOT,
            self.nombre_del_directorio,
            self.nombre_de_archivo
        )

    def crear_archivo_en_directorio(self):
        if self.ya_existe():
            # Esto puede suceder si en un intento previo de depuracion, el
            # proceso es abortado, y por lo tanto, el archivo puede existir.
            logger.warn(_("CrearArchivoDeReporteCsv: Ya existe archivo "
                          "CSV de reporte para la campana "
                          "{0}. Archivo: {1}. El archivo sera "
                          "sobreescrito".format(self._campana.pk, self.ruta)))

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo
        )

    def _escribir_csv_writer_utf_8(self, csvwriter, datos):
        lista_datos_utf8 = [force_text(item) for item in datos]
        csvwriter.writerow(lista_datos_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)

    def escribir_archivo_datos_csv(self):
        # TODO: Debe listar los llamadas contactados: EVENTOS_FIN_CONEXION
        # Agregarle a los llamadas los datos del (posible) contacto
        # Creamos csvwriter
        with open(self.ruta, 'w', newline='', encoding='utf-8') as csvfile:
            csvwiter = csv.writer(csvfile)
            for registro in self.datos_reporte:
                self._escribir_csv_writer_utf_8(csvwiter, registro)


class ExportacionReporteCSV(object):

    def obtener_url_reporte_csv_descargar(self, campana, nombre_reporte):
        archivo_de_reporte = CrearArchivoDeReporteCsv(
            campana,
            nombre_reporte,
            None
        )
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga
        # Esto no debería suceder.
        logger.error(_("obtener_url_reporte_csv_descargar():"
                       "NO existe archivo CSV de descarga "
                       "para la campana {0}".format(campana.nombre)))
        assert os.path.exists(archivo_de_reporte.url_descarga)

    def exportar_reportes_csv(
        self, campana,
        datos_contactaciones_todos=None,
        datos_contactaciones=None
    ):

        if datos_contactaciones is not None:
            # Reporte de resultados de base contactados
            archivo_de_reporte = CrearArchivoDeReporteCsv(
                campana,
                "reporte_resultados",
                datos_contactaciones
            )
            archivo_de_reporte.crear_archivo_en_directorio()
            archivo_de_reporte.escribir_archivo_datos_csv()

        if datos_contactaciones_todos is not None:
            # Reporte de resultados de base contactados
            archivo_de_reporte = CrearArchivoDeReporteCsv(
                campana,
                "reporte_resultados_todos",
                datos_contactaciones_todos
            )
            archivo_de_reporte.crear_archivo_en_directorio()
            archivo_de_reporte.escribir_archivo_datos_csv()
