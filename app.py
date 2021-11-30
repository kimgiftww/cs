# Copyright (c) 2021 Casmatt Co., Ltd.
# All rights reserved. No warranty, explicit or implicit, provided.

from requirements import *
from layout import init_dashboard

# app = Dash(__name__)

app = init_dashboard('app', 'dash_tqm')
app.run_server(debug=True, port=5000)