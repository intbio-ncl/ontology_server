class PreparedQuery:
    def __init__(self,SELECT=None,FROM=None,WHERE=None):
        self._select = SELECT
        self._from = FROM
        self._where = WHERE
        self._filters = []
    
    def build(self):
        qry_str = ""
        if self._select is not None:
            qry_str = f'SELECT {self._select}'
        if self._from is not None:
            qry_str = qry_str + f' FROM <{self._from}>'
        if self._where is not None:
            qry_str = qry_str + f' WHERE {{ {self._where}' 

        for _filter in self._filters:
            qry_str = qry_str + f' FILTER {_filter}'
        qry_str = qry_str + "}"  
        return qry_str
    
    def add_filter(self,filter_str):
        self._filters.append(filter_str)

    @classmethod
    def create_contains_filter(self,identifier_pos,string):
        return f'contains(lcase(str(?{identifier_pos})),"{string}")'