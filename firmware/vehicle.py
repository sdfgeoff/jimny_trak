import time
import machine



def get_vehicle():
    """ Construction function for the vehicles hardware. Handles mapping pins
    to functionality """
    left_track = MotorChannel(
        machine.PWM(machine.Pin(12, machine.Pin.OUT)),
        machine.PWM(machine.Pin(13, machine.Pin.OUT))
    )
    right_track = MotorChannel(
        machine.PWM(machine.Pin(14, machine.Pin.OUT)),
        SoftwarePWM(machine.Pin(16, machine.Pin.OUT))
    )
    lights = machine.Pin(4)

    vehicle = TrackedVehicle(
        left_track,
        right_track,
        lights,
    )
    vehicle.set_speed(0, 0)
    vehicle.set_lights(0)


    return vehicle




class SoftwarePWM:
    """ Uses a software/RTOS timer to create a PWM channel. Current implementation
    is accurate to 5ms. It could probably be improved """
    def __init__(self, pin, duty=0, freq=60):
        self.pin = pin
        self._duty_percent = duty / 1024
        self._period = 1 / freq
        self.timer = machine.Timer(-1)
        self.timer.init(period=5, mode=machine.Timer.PERIODIC, callback=self.update)

    def update(self, _):
        """ Update the software PWM """
        cycle_duration = (time.ticks_ms() / 1000) % self._period
        cycle_percent = cycle_duration / self._period

        if cycle_percent > self._duty_percent:
            self.pin.off()
        else:
            self.pin.on()

    def duty(self, val):
        """ Sets the duty cycle"""
        self._duty_percent = val / 1024


class MotorChannel:
    """ Control a single motor channel. Used with the DRV8833 driver """
    def __init__(self, pwm1, pwm2):
        self.pwm1 = pwm1
        self.pwm2 = pwm2

    def set_speed(self, speed):
        """Sets teh speed from -1 to 1"""
        assert speed >= -1
        assert speed <= 1

        abs_speed = int(abs(speed) * 1024)
        if speed > 0:
            self.pwm1.duty(abs_speed)
            self.pwm2.duty(0)
        else:
            self.pwm1.duty(0)
            self.pwm2.duty(abs_speed)

    def set_brake(self, brake):
        """Enables the brake percentage (0-1)"""
        assert brake >= 0
        assert brake <= 1

        self.pwm1.duty(brake*1024)
        self.pwm2.duty(brake*1024)

class TrackedVehicle:
    """ Control over a vehicle with two tracks """
    def __init__(self, left_track, right_track, lights):
        self.left_track = left_track
        self.right_track = right_track
        self.lights = lights

    def set_speed(self, speed, turn):
        """ Set the speed of the vehicle"""
        self.left_track.set_speed(clamp(speed + turn, -1, 1))
        self.right_track.set_speed(clamp(speed - turn, -1, 1))

    def set_lights(self, val):
        """ Turns the vehicles lights on or off """
        self.lights.value(val)

    def get_battery(self):
        return 0.0


def clamp(value, min_val, max_val):
    """ Ensures a number is between min and max """
    return max(min(value, max_val), min_val)
