import pint
ureg = pint.UnitRegistry()
ureg.define('CAD = [currency]')
ureg.define('USD = 1.35 * CAD')

PV_efficiency = 200 * ureg.watt / (ureg.meter ** 2)
solar_hours_per_day = 7 * ureg.hour / ureg.day
PV_cost_per_area = 80 * ureg.USD / ureg.meter ** 2 # TODO: include mast & spars & rigging

battery_capacity_cost = 200 * ureg.USD / (1.280 * ureg.kilowatt * ureg.hour)

class VesselBase(object):

    def hull_speed(self):
        L_ft = self.LWL.to('foot').magnitude
        return 1.34 * (L_ft ** .5) * ureg.knot

    @property
    def LWL(self):
        try:
            return self._LWL
        except AttributeError:
            print(self, 'Warning: using length for LWL')
            return self.length

    @LWL.setter
    def LWL(self, val):
        val.to('m') # type check, ignore value
        self._LWL = val

    @property
    def sustained_PV_power(self):
        return (self.solar_sail_area * solar_hours_per_day * PV_efficiency).to('kilowatts')

    @property
    def average_wind_power(self):
        return self.sustained_PV_power # guessing - to be evaluated in testing & theory

    @property
    def average_total_power(self):
        return self.sustained_PV_power + self.average_wind_power

    @property
    def PV_cost(self):
        return PV_cost_per_area * self.solar_sail_area

    @property
    def battery_capacity_required(self):
        # kind of a made-up formula that also includes efficiency losses of charging and dis-charging
        #
        # TODO: calculate instead as power required per day - minimum PV production per day
        return .80 * self.sustained_PV_power * 24 * ureg.hours

    @property
    def battery_cost(self):
        return self.battery_capacity_required * battery_capacity_cost
