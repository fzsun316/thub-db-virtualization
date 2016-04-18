from myapp import scheduler
scheduler.start()

from myapp import app

app.run(host='0.0.0.0', debug=True)