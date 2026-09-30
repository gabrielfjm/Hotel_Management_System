"""Pequena ponte para executar Flask-SQLAlchemy 2.1 em Python moderno.

O código de negócio de terceiros permanece inalterado. A dependência original
usa ``time.clock``, removido do Python 3.8. ``perf_counter`` tem o mesmo uso
para a medição interna de tempo daquela dependência.
"""

import time

if not hasattr(time, "clock"):
    time.clock = time.perf_counter
