import multiprocessing

bind = "0.0.0.0:9005"  # The IP and port Gunicorn will listen on
workers = multiprocessing.cpu_count() * 2 + 1  # Number of worker processes
