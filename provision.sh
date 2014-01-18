#!/bin/bash
apt-get update
apt-get install -y -q python-pip python-dev
pip install fabric cuisine

#fab deploy