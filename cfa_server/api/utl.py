from api.log import *
import uuid
import os


def local_update(instance, json_data, ignore=None):
    log.info("ENTERED")
    try:
        for field, value in json_data.items():
            if hasattr(instance, field):
                log.debug(" adding for field name:", field, " with value :", value)
                if ignore is not None:
                    if field not in ignore:
                        setattr(instance, field, value)
                else:
                    setattr(instance, field, value)
    except Exception as e:
        log.warn("Exiting with exception :", e.args)
        print(" Conversion error :", e.args)
    log.info("Returning with success")
    return instance


def get_upload_path(instance, filename):
    """Generate a unique filename for the uploaded file."""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(f"uploads/{instance.mtype}/", filename)
