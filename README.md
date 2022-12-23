# calibre-auto-encode

A Python script to auto-encode the downloaded ePub files.

This script watches the Calibre Content Server library folder and auto-encodes the ePub files to UTF-8. Certain characters showing up on Kindles as weird symbols due to a lack of explicit character encoding declaration [is a known issue](https://www.reddit.com/r/ebooks/comments/wf02l1/why_is_apostrophe_appearing_as_a%C3%A2s_how_can_i/).

I don't run Calibre desktop application, so the only way to force the UTF-8 encoding is using Calibre CLI tools. I didn't want to have to run this manually  every time I downloaded a book via readarr, so I wrote this lil script.

1. Watches the Calibre library directory and subdirectories for creation of new *.epub files.
2. If a new *.epub file is detected, Calibre CLI tool is run to force UTF-8 encoding on the ePub file.
3. The modified file overwrites the original file.

Credit to [mastro35](https://github.com/mastro35) for the inspo and [helping me get started with this project](https://thepythoncorner.com/posts/2019-01-13-how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/). 
