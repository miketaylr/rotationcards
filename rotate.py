#!/usr/bin/env python

import datetime
import json
import os

import click
from dotenv import load_dotenv
import requests

load_dotenv()

OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
# this is the project ID for web-bugs rotation project
# see https://developer.github.com/v3/projects/
PROJECT_ID = os.getenv('PROJECT_ID')
COLUMNS = [
    '5301985',  # karl
    '5051659',  # dennis
    '5051665',  # ksenia
    # 7064653, # mike
    # 5051664, # tom
]

HEADERS = {
    'Authorization': 'token {0}'.format(OAUTH_TOKEN),
    'Accept': 'application/vnd.github.inertia-preview+json',
    'User-Agent': 'miketaylr/rotationcards'
}

# GET /repos/:owner/:repo/projects -- this gets the project ID
# curl -H "Accept: application/vnd.github.inertia-preview+json" -H "Authorization: token OAUTH_TOKEN_HERE" https://api.github.com/repos/miketaylr/test/projects
# to get the ID, then we have to get column keys from that.
# curl -H "Accept: application/vnd.github.inertia-preview+json" -H "Authorization: token OAUTH_TOKEN_HERE" https://api.github.com/projects/4032465/columns

# Here's a horrible global variable
first = False
# TODO: make a generator that returns the next working day
# then we can skip this global crap


@click.command()
@click.option('--firstdate', prompt='The first weekday to start with',
              help='The first weekday to start with. Format: YYYY-MM-DD')
def make_cards(firstdate):
    """Takes the first date and makes a set of cards for each given column."""
    click.echo("OK, making cards starting with {0}".format(firstdate))
    global first
    if not first:
        first = firstdate
    for column in COLUMNS:
        create_card(get_two(first), column)


def get_next_workday(today, set_global=True):
    tomorrow = today + datetime.timedelta(days=1)
    if tomorrow.isoweekday() in set((6, 7)):
        tomorrow += datetime.timedelta(days=8 - tomorrow.isoweekday())
    if set_global:
        global first
        first = get_next_workday(tomorrow, False).strftime('%Y-%m-%d')
    return tomorrow


def get_two(firstdate):
    """Return the 2 days we want to create assignments for, as a tuple."""
    try:
        day = datetime.datetime.strptime(firstdate, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect firstdate format, should be YYYY-MM-DD")
    return (day.strftime('%a, %b %d'),
            get_next_workday(day).strftime('%a, %b %d'))


def create_card(date_tuple, column_id):
    """Make the GitHub request to create the card.
    POST /projects/columns/:column_id/cards
    params: note (string)
    """
    uri = 'https://api.github.com/projects/columns/{0}/cards'.format(
        column_id)
    full_body = '* [ ] {0}\n* [ ] {1}'.format(*date_tuple)

    rv = requests.post(uri, data=json.dumps(
        {"note": full_body}), headers=HEADERS)
    click.echo(rv.status_code)


if __name__ == '__main__':
    make_cards()
