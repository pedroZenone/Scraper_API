# Scraper_API

Here are some bots and API connections to get data.

- Twitter API: This code let you connect to Twitter API and get tweets from users, and get metadata
of each users. Because getting user data is slow, I only get the ids and then the metadata
in chunks of 100 users

- Twitter Scraper: Because twitter only allows donwloading tweets up to 7 days back, I used a third development that scraps twitter using selenium letting the program bring historical data. The problem of this library is that when you do lots of queries it sometimes get stucked or throw connection errors, so I had to implement a supervisor program that creates sub processes that call the twitter scraper program. If this process get stucked the master will kill him and continue.

- Tuenti: This is a crawler I developed to obtain the whole data of Tuenti's forum. The final porduct was a visualization of wordclouds clustered by topic of thread.

- Facebook Images: GraphAPI dont give you the creative link of the post, so if you would like to understand why your creative is performing better or worse you have to download it. This bot download the image from a post (the magic here is to enter to mobile page!!)

- DCM: This scrpit that connects to DCM platform and downloads the creatives. then I download manually the report and join the id of image with the metrics.

- Admetricks: Connection to admetricks service and dowload of reports.
