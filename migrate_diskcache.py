#!/usr/bin/env python3
from diskcache import Index, JSONDisk
import os
import shutil


directory = 'config/panelindexcache'
directory2 = 'config/panelindexcache_json'


def migrate() -> None:
    index = Index(directory)
    index_json = Index(directory2, disk=JSONDisk)

    for key in index.keys():
        try:
            value = index.get(key)
        except ModuleNotFoundError:
            print(f'Error migrating key `{key}`')
            continue

        index_json[key] = value
        print(f'Migrating key `{key}`')

    shutil.rmtree(directory)
    os.rename(directory2, directory)


if __name__ == '__main__':
    migrate()
