from api.log import *
def local_update(instance, json_data):
    log.info("ENTERED")
    try:
        for field, value in json_data.items():
            if hasattr(instance,field):
                log.debug(" adding for field name:",field, " with value :",value)
                setattr(instance,field,value)
    except Exception as e:
        log.warn("Exiting with exception :",e.args)
        print(" Conversion error :",e.args)
    log.info("Returning with success")
    return instance