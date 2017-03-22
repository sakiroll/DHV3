import sqlite3
import logging

def dictrow(row):
    return dict(zip(row.keys(), row))

print("Correction des données...")

# Fix données
db = sqlite3.connect("scores.db")
db.isolation_level = None
db.row_factory = sqlite3.Row
sql = db.cursor()

tables = sql.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

columns = [
    'shoots_fired',
    'shoots_missed',
    'shoots_no_duck',
    'tirsManques',
    'tirsSansCanards'
]

sql.execute("BEGIN")
for table in tables:
    for column in columns:
        try:
            sql.execute("ALTER TABLE '{0}' ADD COLUMN {1}".format(table['name'], column))
        except:
            pass
sql.execute("COMMIT")

try:
    sql.execute("BEGIN")

    for table in tables:
        users = sql.execute("SELECT * FROM '{0}'".format(table['name'])).fetchall()
        for user in users:
            user = dictrow(user)
            print(table['name'])
            sql.execute("UPDATE '{0}' SET shoots_fired=:shoots_fired, shoots_missed=:shoots_missed, shoots_no_duck=:shoots_no_duck, tirsManques=NULL, tirsSansCanards=NULL WHERE id_=:id_".format(table['name']), { \
                'shoots_fired': ((user.get('tirsManques', 0) or 0) \
                    + (user.get('tirsSansCanards', 0) or 0) \
                    + (user.get('shoots_no_duck', 0) or 0) \
                    + (user.get('canardsTues', 0) or 0) \
                    + (user.get('shoots_harmed_duck', 0) or 0) \
                    + (user.get('shoots_frightened', 0) or 0)), \
                'shoots_missed': (user.get('tirsManques', 0) or 0), \
                'shoots_no_duck': ((user.get('shoots_no_duck', 0) or 0) \
                    + (user.get('tirsSansCanards', 0) or 0)), \
                'id_': user['id_']})
            print("Données de l'utilisateur {0} corrigées sur la table {1}.".format(user['name'], table[0]))
        print("Données de la table {0} corrigées.".format(table[0]))

    print("Veuillez patienter...")
    sql.execute("COMMIT")
except:
    logging.exception("Erreur !")
    sql.execute("ROLLBACK")

print("Correction des données terminée.")
print("")
print("Correction des colonnes...")

# Fix colonnes
renameColumns = {
    'superCanardsTues': 'killed_super_ducks',
    'canardsTues':            'killed_ducks',
    'chasseursTues':        'killed_players',
    'meilleurTemps':             'best_time',
    'AssuranceVie':         'life_insurance',
    'munExplo':             'explosive_ammo',
    'tirsManques':             'IGNORE_ME_1',
    'tirsSansCanards':         'IGNORE_ME_2'
}

try:
    sql.execute("BEGIN")
    sql.execute("PRAGMA writable_schema=1")

    for table in tables:
        for old, new in renameColumns.items():
            sql.execute("UPDATE sqlite_master SET SQL=REPLACE(SQL, '{0}', '{1}') WHERE name='{2}'".format(old, new, table[0]))
            print("{0} renommé en {1} sur {2}.".format(old, new, table[0]))

    sql.execute("PRAGMA writable_schema=0")
    print("Veuillez patienter...")
    sql.execute("COMMIT")
except:
    print("Erreur !")
    sql.execute("ROLLBACK")

print("Correction des colonnes terminée.")
print("")
print("Base de données corrigée ! Analyse...")
sql.execute('ANALYZE')
print("Analyse terminée.")
