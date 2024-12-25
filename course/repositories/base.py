import os
from typing import Union


class Pagination:
    __page: int = 1
    __page_size: int = 100

    __max_page_size: int = int(os.getenv("MAX_PAGE_SIZE", '1000'))

    def __init__(self, page: int = 1, per_page: int = 10):
        self.page = max(1, page)
        self.per_page = max(1, per_page)

    @property
    def page(self) -> int:
        return self.__page

    @page.setter
    def page(self, value: int) -> None:
        self.__page = max(1, value)

    @property
    def page_size(self) -> int:
        return self.__page_size

    @page_size.setter
    def page_size(self, value: int) -> None:
        self.__page_size = min(self.__max_page_size, value)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


class OrderBy:
    _allows_fields = ()
    _default_order_by = ()

    def __init__(self, fields=None):
        self.fields = fields if fields else self._default_order_by
        if not isinstance(self.fields, (list, tuple)):
            self.fields = [self.fields]
        self._validate()

    def _validate(self):
        for field in self.fields:
            if field not in self._allows_fields:
                raise ValueError(f"Order by field '{field}' not allowed")
