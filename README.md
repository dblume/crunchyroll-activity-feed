[![License](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://raw.githubusercontent.com/dblume/crunchyroll-activity-feed/main/LICENSE)
![python3.x](https://img.shields.io/badge/python-3.x-green.svg)

## Crunchyroll Activity Feed

You can create a Crunchyroll activity feed with this script. Activity feeds are
records of the things you've done. In this case, it's a list of episodes
you've watched.

Activity feeds can be used to collect data for lifestreaming and for the Quantified
Self projects.

## Getting Started

1. Install the required module(s):  `python3 -m pip install -r requirements.txt`
2. Rename crunchyroll\_feed.cfg.sample to crunchyroll\_feed.cfg.
3. Customize the variables in crunchyroll\_feed.cfg. (More on this below.)
4. Set up a cronjob that runs crunchyroll\_feed.py once every day.

You can specify an output file for logs with the -o flag, like so:

    ./crunchyroll_feed.py -o crunchyroll.log

The feed will be written to the filename specified in crunchyroll\_feed.cfg, in this
example, it'd be an RSS feed named "crunchyroll-activity.xml"

## How it works

It logs in as you in Crunchyroll, and then makes an activity feed of the last
few shows you streamed.

## Customizing crunchyroll\_feed.cfg

The configuration file looks like this:

    [main]
    username = user@example.org
    password = correcthorsebatterystaple
    [feed]
    filename = crunchyroll-activity.xml
    href = http://domain.org/%(filename)s
    title = My Crunchyroll Activity Feed

Replace username and password with your Crunchyroll username and password. Set the
feed filename, location, and title as you like.

### Protect your password

If crunchyroll\_feed.cfg is present on your server that's serving the RSS feed, be sure
to deny access to it. If you have a .htaccess file, you can do so with

    <Files ~ "\.cfg$">
    Order allow,deny
    Deny from all
    </Files>


## An example feed

Here's [an example feed](http://feed.dlma.com/crunchyroll-activity.xml). It [meets RSS validation requirements](https://validator.w3.org/feed/check.cgi?url=http%3A//feed.dlma.com/crunchyroll-activity.xml). &check;

## Creating a feed from JSON files directly

You can save JSON files and pass them in to `crunchyroll_feed.py`.

1. From Chrome, open Inspect at Crunchyroll's main page.
2. Select the Inspector's Network tab, and ensure it's recording. Optionally filter for the term `page_size`.
3. Navigate to your History page from your Profile icon at the top right.
4. In the Inspector, select the request with `page_size`, and then select its Preview tab.
5. Copy the JSON (both "Copy Value" and "Copy Object" work) and save it to file.
6. Optionally scroll down in the History to retrive more JSON pages and save them too.

Then run the script with the saved files as arguments:

    ./crunchyroll_feed.py page1.json page2.json

## Is it any good?

[Yes](https://news.ycombinator.com/item?id=3067434).

## Licence

This software uses the [Apache License 2.0](https://raw.githubusercontent.com/dblume/crunchyroll-activity-feed/main/LICENSE)
