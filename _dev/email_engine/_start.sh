#!/bin/bash
set -xv
lamson stop -ALL run/
lamson start
lamson log
