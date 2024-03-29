#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def _find_project(try_dir=None, max_depth=5):
    if not try_dir or max_depth == 0:
        raise Exception('Could not find project top directory')
    if os.path.isfile(os.path.join(try_dir, '.%s.top' % PROJECT_NAME)):
        return os.path.abspath(try_dir)
    return _find_project(os.path.join(try_dir, os.path.pardir), max_depth=max_depth - 1)

PROJECT_NAME = 'emag'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '%s.settings' % PROJECT_NAME)

TOP_DIR = _find_project(os.path.dirname(os.path.realpath(__file__)))
BASE_APP_DIR = os.path.join(TOP_DIR, PROJECT_NAME)
DATA_DIR = os.path.join(TOP_DIR, 'var')
