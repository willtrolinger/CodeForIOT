import cherrypy
from threading import Thread

from Sensors import Sensors

sensor_obj = Sensors()
sensors = sensor_obj.sensors
ir_loop = Thread(target=sensor_obj.run_ir)
ir_loop.start()
therm_loop = Thread(target=sensor_obj.run_therm)
therm_loop.start()
motor_loop = Thread(target=sensor_obj.run_motor)
motor_loop.start()


template = \
"""
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    </head>
    <header>
        <div class="navbar navbar-dark bg-dark shadow-sm" style="height:50px;">
        </div>
    </header>
    <body>
    <section class="py-5 text-center container">
        <div class="row py-lg-5">
            <div class="col-lg-6 col-md-8 mx-auto">
                <h1 class="fw-light"> IOT Dashboard </h1>
                <p class="lead text-muted">Jake Parnell, Kel Howell, Will Trolinger</p>
            </div>
        </div>
    </section>
    
        <div class="album py-5 bg-light">
            <div class="container">
                <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-3">
                
                    {tbl}
                
                </div>
            </div>
        </div>
    </body>
</html>
"""

def generate_sensor_card(sensors=sensors):
    cards = ""

    for sensor in sensors:
        if sensor == "Thermometer":
            card = \
            """
                <div class="col">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <p class="card-text">{sns}:</p>
                            <p class="card-text">{temp} C</p>
                            <div class="d-felx justify-content-between-align-items-center">
                                <form action='toggleSensor' method='POST'>
                                    <input type='hidden' name='sensor' value='{sns}'>
                                    <input type='submit' value='Refresh' class='btn btn-primary'>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            """
            running_status = sensor_obj.sensors[sensor]
            if running_status is True:
                temperature = sensor_obj._getTemp()
                temperature = round(temperature, 1)
                card = card.format(sns=sensor, temp=temperature)
            else:
                temperature = sensor_obj._getTemp()
                temperature = round(temperature, 1)
                card = card.format(sns=sensor, temp=temperature)
            cards = cards + card
            
        elif sensor == "Motor":
            card = \
            """
                <div class="col">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <p class="card-text">{sns}</p>
                            <p class="card-text">Is on: {status}</p>
                            <div class="d-felx justify-content-between-align-items-center">
                                <form action='turn_left' method='POST'>
                                    <input type='hidden' name='sensor' value='{sns}'>
                                    <input type='submit' value='Turn Left' class='btn btn-primary'>
                                </form>
                                <form action='turn_right' method='POST'>
                                    <input type='hidden' name='sensor' value='{sns}'>
                                    <input type='submit' value='Turn Right' class='btn btn-primary'>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            """
            card = card.format(sns=sensor, status="Running")
            cards = cards + card
        else:    
            card = \
            """
                <div class="col">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <p class="card-text">{sns}</p>
                            <p class="card-text">Status: {status}</p>
                            <div class="d-felx justify-content-between-align-items-center">
                                <form action='toggleSensor' method='POST'>
                                    <input type='hidden' name='sensor' value='{sns}'>
                                    <input type='submit' value='Toggle' class='btn btn-primary'>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            """
            running_status = sensor_obj.sensors[sensor]
            if running_status is True:
                card = card.format(sns=sensor, status="On")
            else:
                card = card.format(sns=sensor, status="Off")
            cards = cards + card
    return template.format(tbl = cards)

class Dashboard(object):
    @cherrypy.expose
    def index(self):
        html = generate_sensor_card()
        return html

    @cherrypy.expose
    def toggleSensor(self, sensor):
        sensor_obj.sensors[sensor] = not sensor_obj.sensors[sensor]
        
        html = generate_sensor_card()
        return html

    @cherrypy.expose
    def turn_left(self, sensor):
        sensor_obj._turnLeft()
        html = generate_sensor_card()
        return html
    
    @cherrypy.expose
    def turn_right(self, sensor):
        sensor_obj._turnRight()
        html = generate_sensor_card()
        return html
cherrypy.quickstart(Dashboard())
