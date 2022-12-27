# calibre-auto-encode

## Overview

A Python script to auto-encode the downloaded ePub files. This script is meant to be deployed in a NAS workflow involving [Readarr](https://readarr.com/), [sabnzbd](https://sabnzbd.org/), and [Calibre Content Server](https://calibre-ebook.com/new-in/twelve).

## Details

This script watches the Readarr download directory and auto-encodes the ePub files to UTF-8. Certain characters showing up on Kindles as weird symbols due to a lack of explicit character encoding declaration [is a known issue](https://www.reddit.com/r/ebooks/comments/wf02l1/why_is_apostrophe_appearing_as_a%C3%A2s_how_can_i/). The script then uses the Calibre commandline tool to import the newly encoded ePub into your Calibre library.

I don't run Calibre desktop application, so the only way to force the UTF-8 encoding is using Calibre CLI tools. I didn't want to have to do this manually  every time I downloaded a book via Readarr.

I had originally designed this to have Watchdog look for *.epub file creation events in the Calibre library directory. But due to Calibre's renaming and importing workflow, it introduced too much unpredictability. Specifically, Watchdog module was not predictably catching renamed ePub files during file creation and folder rename/move events.

### Workflow

1. Watches the sabnzbd download directory and subdirectories for creation of new *.epub files.
2. If a new *.epub file is detected, Calibre CLI tool is run to force UTF-8 encoding on the ePub file.
3. The modified file overwrites the original file.
4. The motified file is added to the Calibre library.

## Recommended Workflow Setup

1. Install the script in your Calibre Content Server jail.
2. Do not enable Calibre integration in your Readarr's Media Management setup.
3. Do not enable automatic importing of your ePub in Readarr's Download Clients setup.
4. Enable this script as a boot up service.

## Credits

To [mastro35](https://github.com/mastro35) for the inspo and [helping me get started with this project](https://thepythoncorner.com/posts/2019-01-13-how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/).