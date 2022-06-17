class _Prettifiable:
    def __init__(self, value, format_str):
        self.value = value
        self.format_str = format_str

    @property
    def pretty(self):
        return self.format_str.format(self.value)

    def __str__(self):
        return self.value

class _Geo:
    UNSET = 1000.0
    
    def __init__(self):
        self.lat = 1000.0
        self.lon = 1000.0
        self.address = 'Ismeretlen cím'
    
    @property
    def map_url(self):
        return f'https://www.google.com/maps?q={str(self.lat)}%2C{str(self.lon)}&z=12'

class Ad:
    title = None
    subtitle = None
    description = None
    photoUrl = None
    url = None
    currency = 'Ft'
    _price = 'N/A'
    _rooms = 'N/A'
    _size = 'N/A'
    geo = _Geo()
    address = None
    seller_name = None
    tel_number = None
    tel_number_pretty = None

    internal_data = None

    @property
    def price(self):
        return _Prettifiable(self._price, '{} ' + self.currency)

    @price.setter
    def price(self, value):
        self._price = str(value)

    @property
    def rooms(self):
        return _Prettifiable(str(self._rooms), '{} szoba')

    @rooms.setter
    def rooms(self, value):
        self._rooms = value

    @property
    def size(self):
        return _Prettifiable(str(self._size), '{} m²')

    @size.setter
    def size(self, value):
        self._size = value

