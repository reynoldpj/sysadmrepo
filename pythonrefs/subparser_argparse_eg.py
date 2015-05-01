#!/usr/bin/env python

import argparse

from pprint import pprint

def createWebargparser(subparser):
    #web commands
    web_parser     =  subparser.add_parser('web')
    web_parser.add_argument('web_command', choices=['domainstat','serverstat'])
    web_parser.add_argument('web_args')

def createMariadbparser(subparser):
    #mariadb commands
    mariadb_parser =  subparser.add_parser('mariadb')
    mariadb_parser.add_argument('mariadb_command', choices=['dbinfo','domainstat','domaininfo','fullproclist'])
    mariadb_parser.add_argument('mariadb_args')

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-v')

    #create subparser
    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands', help='additional help')

    #mariadb cmdline parser
    createMariadbparser(subparsers)

    #web cmdline parser
    createWebargparser(subparsers)

    args = parser.parse_args()

    pprint(args)

if __name__ == "__main__":
    main()
