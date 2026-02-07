from config.database import get_db_connection


class ProvisionModel:
    @staticmethod
    def get_provision_data(semana, tipo_provision):
        conn = get_db_connection()
        cursor = conn.cursor()

        tabla = 'semana_provision_quincenal' if tipo_provision == 'quincenal' else 'semana_provision'

        cursor.execute(f'SELECT * FROM {tabla} WHERE id=%s', (semana,))
        data = cursor.fetchone()

        cursor.close()
        conn.close()
        return data

    @staticmethod
    def get_provision_logs():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT semana, cantAprob, cantRecha, tipoNom, Usuario, fechaProv FROM prov_logs')
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        return logs

    @staticmethod
    def get_provision_totals():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(cantAprob) as total_aprob, SUM(cantRecha) as total_rechazado FROM prov_logs')
        totals = cursor.fetchone()
        cursor.close()
        conn.close()
        return totals
