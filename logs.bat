@echo off
python -c "import sqlite3, datetime, tabulate; conn=sqlite3.connect('astraflux.db'); rows=conn.execute('SELECT github_username, ip_address, login_time FROM login_logs').fetchall(); rows=[(u,ip,datetime.datetime.fromtimestamp(t)) for u,ip,t in rows]; print(tabulate.tabulate(rows, headers=['GitHub User','IP','Login Time']))"
pause
