from myapp import scheduler
scheduler.start()

from myapp import app

app.run(host='0.0.0.0', debug=True)

import myapp.services
services.request_heartbeat()
services.check_traffic_status()
services.check_weather_status()