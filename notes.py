#!/usr/bin/env python3
import sys
from pathlib import Path

NOTES_FILE = Path(__file__).resolve().parent / 'notes.txt'

def add_note(text: str):
    with NOTES_FILE.open('a', encoding='utf-8') as f:
        f.write(text.rstrip('\n') + '\n')

def list_notes():
    if not NOTES_FILE.exists():
        return
    with NOTES_FILE.open('r', encoding='utf-8') as f:
        for line in f:
            print(line.rstrip('\n'))

def print_usage():
    print('Usage: python notes.py add "text"')
    print('       python notes.py list')

def main(argv):
    if len(argv) < 2:
        print_usage()
        return 1
    cmd = argv[1]
    if cmd == 'add':
        if len(argv) < 3:
            print('Error: missing note text')
            return 1
        add_note(' '.join(argv[2:]))
    elif cmd == 'list' or cmd == 'list_broken':
        list_notes()
    else:
        print_usage()
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
