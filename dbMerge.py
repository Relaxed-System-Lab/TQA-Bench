import sqlite3
import argparse

def merge(dst, src):
    dstConn = sqlite3.connect(dst)
    srcConn = sqlite3.connect(src)
    dstCur = dstConn.cursor()
    srcCur = srcConn.cursor()
    srcCur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tableNames = srcCur.fetchall()
    if tableNames:
        tableNames = [item[0] for item in tableNames]
    else:
        return False
    srcCur.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    sqls = srcCur.fetchall()
    if sqls:
        sqls = [item[0] for item in sqls]
    else:
        return False
    for s in sqls:
        dstCur.execute(s)
        dstConn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To combine all result dataset together.')
    parser.add_argument('--dst', type=str, help='The destination sqlite to save all results.')
    parser.add_argument('--src', type=str, nargs='+', help='The list of result sqlite to combine.')
    args = parser.parse_args()
    for src in args.src:
        merge(args.dst, src)
