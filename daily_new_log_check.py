# V_Gabor
# adott felhasználó rejtéseinél megnézi az új logokat és fájlba menti rendezve
# ha nincs korábbi lekérdezés, akkor az előző x napot (default_days) nézi
# dátumnál a log adatbázisba kerülését vizsgálja, így visszadátumozott logokat is megjelenít

# Changelog:
# 2020-11-09 - Start

# TODO: kimenet legyen formázott html? (nem túl szimpatikus ötlet)
# TODO: tartsa nyilván a letöltött logokat JSON-ban a pontosság miatt? (kimenet marad txt)

import json
import requests
import datetime
import os


def num_of_days(date_log, date_last):  # bemenet szövegek: 'YYYY-MM-DD HH:MM:SS' formátumban
    """A date_log és a date_last között eltelt napok számát adja vissza."""
    date1 = datetime.datetime.strptime(date_log, '%Y-%m-%d %H:%M:%S')
    date2 = datetime.datetime.strptime(date_last, '%Y-%m-%d %H:%M:%S')
    return (date2 - date1).days


def main():
    user_id = '15495'  # geocaching.hu felhasználó id-jét kell itt megadni, a többit leszedi
    default_days = 14  # nap; alapeset, ha még nem volt korábban ellenőrzés
    file_name = 'logok.txt'
    file_backup = 'logok-elozo.txt'
    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    full_path_backup = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_backup)

    if os.path.isfile(full_path):
        with open(full_path, encoding='utf-8', mode='r') as f:
            date_last_check = f.readline().rstrip()[:19]
        if os.path.isfile(full_path_backup):
            os.remove(full_path_backup)
            os.rename(full_path, full_path_backup)
        else:
            os.rename(full_path, full_path_backup)
    else:
        date_last_check = str(datetime.datetime.today() - datetime.timedelta(days=default_days))[:19]

    print('Legutóbbi ellenőrzés dátuma:', date_last_check)
    print('Adatok lekérése a geocaching.hu oldalról...')

    gc_api_url = 'https://api.geocaching.hu/cachesbyuser?userid=' + user_id + '&own=true&fields=id'
    user_caches_data = requests.get(gc_api_url).json()  # lekérés

    newlog_nopwd = []
    newlog_notfound = []
    newlog_found = []
    newlog_other = []
    header = []  # ennek nem kellene list-nek lennie, mert csak egy sorból áll a fejléc ;)
    counter = 0

    # mindig az aktuális dátum legyen a következő ellenőrzés ideje
    header.append(str(datetime.datetime.today())[:19] + ' - utolsó ellenőrzés dátuma, melynek eredménye:')

    newlog_nopwd.append('\n\nJelszó nélküli logok:')  # \n\n = 2 üres sor a jobb olvashatóságért
    newlog_notfound.append('\n\nNem találtam meg logok:')
    newlog_found.append('\n\nMegtaláltam logok:')
    newlog_other.append('\n\nEgyéb logok:')

    for cache in user_caches_data:
        gc_api_url = 'https://api.geocaching.hu/logsbycache?cacheid=' + cache[
            'id'] + '&fields=user_id,member,cache_id,logtype,waypoint,nickname,dateinserted,date'
        logs_data = requests.get(gc_api_url).json()  # lekérés

        for data in logs_data:
            if len(data['dateinserted']) > 1:
                # negatív a napok száma, ha az utolsó ellenőrzés dátumától korábbi a log
                if num_of_days(data['dateinserted'], date_last_check) < 0:
                    if data['logtype'] == '1':
                        newlog_found.append('  {:<6} {} {}'.format(data['waypoint'], data['date'], data['member']))
                        counter += 1
                    if data['logtype'] == '2':
                        newlog_nopwd.append('  {:<6} {} {}'.format(data['waypoint'], data['date'], data['member']))
                        counter += 1
                    if data['logtype'] == '3':
                        newlog_notfound.append('  {:<6} {} {}'.format(data['waypoint'], data['date'], data['member']))
                        counter += 1
                    if data['logtype'] == '4':
                        newlog_other.append('  {:<6} {} {}'.format(data['waypoint'], data['date'], data['member']))
                        counter += 1

    # amelyikhez nem került egy adat sem, ott az alábbi szöveg jelenik meg
    nincs_ilyen_log = '    ------ nincs új log'
    if len(newlog_found) == 1:  # ha csak a fejléc szöveg van benne
        newlog_found.append(nincs_ilyen_log)
    if len(newlog_nopwd) == 1:
        newlog_nopwd.append(nincs_ilyen_log)
    if len(newlog_notfound) == 1:
        newlog_notfound.append(nincs_ilyen_log)
    if len(newlog_other) == 1:
        newlog_other.append(nincs_ilyen_log)

    # a következők alapján alakul a fájlba kiírt adatok sorrendje
    with open(full_path, encoding='utf-8', mode='w') as fid:
        for line in header:
            fid.write(line + '\n')
        for line in newlog_nopwd:
            fid.write(line + '\n')
        for line in newlog_notfound:
            fid.write(line + '\n')
        for line in newlog_found:
            fid.write(line + '\n')
        for line in newlog_other:
            fid.write(line + '\n')

    # képernyőre egy kis tájékoztatás
    print('\n{} darab új logot találtam.\n\nAz eredményt a {} fájlban találod.'.format(counter, file_name))
    print('Kérlek, ne töröld, mert a következő lekérést a fájl alapján végzi a program!')
    print('\nAz előző lekérdezés eredményét a {} nevű fájlban találod (ha volt ilyen). Ezt bármikor törölheted.'
          .format(file_backup))
    print('Amennyiben nincs érvényes logok.txt fájl, úgy a legutóbbi {} napot nézzük.'.format(default_days))
    a = input('\nENTER-re vége.')


if __name__ == '__main__':
    # csak akkor fut, ha nem modul
    main()
