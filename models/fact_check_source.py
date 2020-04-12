class FactCheckSource:

    def __init__(self, name, fact_checks):
        self.name = name
        self.fact_checks = fact_checks
        self.num_fact_checks = len(fact_checks)