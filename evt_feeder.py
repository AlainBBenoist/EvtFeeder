import sys
import os
import codecs
import csv
import logging
from pathlib import Path, PurePath

import tools
from scrap_decorators import evt_collector, get_evt_collectors, evt_parser, get_evt_parsers
from scrappers import *

logger = logging.getLogger(__name__)

## TODO :
## Afficher le nombre d'évenements tenus sur un lieu quand on propose un choix de lieu

class evt_feeder() :
    """
    This class will iterate through a list of URLs containing events as retrieved by specialized web collectors
    """
    def __init__(self, collectors, evt_categories, evt_regions, filter_function) :
        # Initializing the list of collectors
        self.collectors = collectors

        # Search criteria
        self.evt_categories = evt_categories
        self.evt_regions = evt_regions
        self.filter_function = filter_function
        
        # Initializing counters
        self.ncollectors, self.icollector = len(self.collectors), 0                 # Number of collectors
        self.nurls = self.iurl = 0                                                  # Number of urls and index of current url
        self.n_proc = self.n_submitted = 0                                          # Number of URLs processed and parsed

        # Load the page parsers 
        self.parsing_table = get_evt_parsers()                                      # the parsers will retrieve events detailed informations
        logger.debug(self.parsing_table) 
        
    def __iter__(self) :      
        # The URL collectors are called one by one to gather a list of events URL
        for collector in self.collectors :
            self.icollector += 1
            # Retrieve the list of URLs containing event details
            collected_urls = collector(self.evt_categories, self.evt_regions)
            if collected_urls :
                self.nurls = len(collected_urls)
                self.iurl = 0
                # Processing each URL
                for url in collected_urls :
                    self.iurl += 1
                    self.n_proc += 1
                    # Some of them might be just filtered
                    if self.filter_function and self.filter_function(url) :
                        logger.info('[{:4d}] Skipping {:s}'.format(self.n_proc, url))            
                        continue
                    else :
                        # Find the parser for the URL and integrate the event 
                        for upt in self.parsing_table :
                            if ( url.startswith(upt) ) : # Found a matching rule
                                # retrieve the events details from the web page by calling the parsing function matching the url 
                                evt_info = self.parsing_table[upt](url)
                                if evt_info :
                                    self.n_submitted += 1
                                    yield evt_info
                                break
                        else :
                            logger.warning('No matching rule for {:s}'.format(url))

if __name__ == '__main__' :
    attributes = ['name',
                  'description',
                  'start_date',
                  'end_date',
                  'venue_name',
                  'address',
                  'zipcode',
                  'city',
                  'cost',
                  'evt_media',
                  'evt_category',
                  'email',
                  'telephone',
                  'raw_address',
                  'tag',
                  'source_url',
                  'class',
                  'publisher_name',
                  'publisher_logo',
                  'publisher_url',
                  'created_by',
                   ]
    stem = os.path.splitext(os.path.basename(__file__))[0]
    logging.basicConfig(filename=stem+'.log',
                        filemode='w',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)-10s %(module)s:%(lineno)03d %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    # Ask the collectors we want to use
    collectors = []
    for collector in get_evt_collectors() :
        key = input('Launch {:s} (o/n) ? '.format(collector.__name__))
        if key in ['o', 'O', 'y', 'Y' ] :
            collectors.append(collector)

    logger.debug(collectors)
    # Search criteria
    evt_categories = ['expositions', 'stages']
    evt_regions = ['ile-de-France', 'paris']

    # Retrieve selected events
    n_events = 0
    for evt_info in evt_feeder(collectors, evt_categories, evt_regions, None):
        try :
            print('{:s} {:s}-{:s} [{:32.32s}]'.format(evt_info['name'], evt_info['start_date'], evt_info['end_date'], evt_info['source_url']))
            n_events += 1
        except :
            pass
    print('{:d} events retrieved'.format(n_events))
