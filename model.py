class _Prettifiable:
    def __init__(self, value, format_str):
        self.value = value
        self.format_str = format_str

    @property
    def pretty(self):
        return self.format_str.format(self.value)

    def __str__(self):
        return self.value


class Ad:
    title = None
    subtitle = None
    description = None
    photoUrl = None
    url = None
    _price = _Prettifiable('N/A', '{} Ft')
    currency = 'Ft'
    _rooms = _Prettifiable('N/A', '{} szoba')
    _size = _Prettifiable('N/A', '{} m²')
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

