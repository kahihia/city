import os
from django.contrib.gis.utils import LayerMapping
from event.models import CountryBorder

world_mapping = {
    'code' : 'ISO2',
    'name' : 'NAME',    
    'mpoly' : 'MULTIPOLYGON',
}

world_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/TM_WORLD_BORDERS-0.3.shp'))

def run(verbose=True):
    lm = LayerMapping(CountryBorder, world_shp, world_mapping,
                      transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)