import os
import csv
import logging
import datetime
import obd.obd as obd

logging.basicConfig(
    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG,
)

obd.debug.console = True
connected = False
while not connected:
    try:
        logging.info('attempting to connect...')
        o = obd.OBD()
        logging.info('connected to OBD2!!!!')
        logging.info(o.print_commands())
        connected = True
        obd.debug.console = False
    except Exception as e:
        logging.error('exception on connection: {}'.format(e))


def get_logname():
    return datetime.datetime.now().strftime('%Y%m%d-%H%m%S')


def resp_to_dict(resp):
    d = {}
    if resp is None:
        return d
    cmd = resp.command
    d['cmd'] = cmd.command if cmd else None
    d['command_name'] = cmd.name if cmd else None
    d['ecu'] = cmd.ecu if cmd else None
    d['value'] = str(resp.value)
    d['unit'] = str(resp.unit)
    d['time'] = resp.time
    return d


commands = [
    obd.commands.RPM,
    obd.commands.SPEED,
    obd.commands.THROTTLE_ACTUATOR,
    obd.commands.THROTTLE_POS,
    obd.commands.THROTTLE_POS_B,
    obd.commands.RELATIVE_THROTTLE_POS,
    obd.commands.ACCELERATOR_POS_D,
    obd.commands.ACCELERATOR_POS_E,
    obd.commands.MAF,
    obd.commands.ENGINE_LOAD,
    obd.commands.COOLANT_TEMP,
    obd.commands.INTAKE_TEMP,
    obd.commands.EVAPORATIVE_PURGE,
    obd.commands.SHORT_FUEL_TRIM_1,
    obd.commands.SHORT_FUEL_TRIM_2,
    obd.commands.TIMING_ADVANCE,
]


with open('{}.csv'.format(get_logname()), 'w') as csv_logfile:
    fieldnames = resp_to_dict(obd.OBDResponse()).keys()
    writer = csv.DictWriter(csv_logfile, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()

    while True:
        for cmd in commands:
            try:
                resp = o.query(cmd)
                d = resp_to_dict(resp)
                writer.writerow(d)
                logging.debug(d)
            except Exception as e:
                logging.error('got exception {}'.format(e))
                raise
